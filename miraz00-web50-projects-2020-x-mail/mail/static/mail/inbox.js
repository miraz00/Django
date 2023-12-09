document.addEventListener('DOMContentLoaded', function() {

  const inboxButton = document.getElementById('inbox')
  inboxButton.classList.remove("btn-outline-primary")
  inboxButton.classList.add("btn-primary")

  // Use buttons to toggle between views
  inboxButton.addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archive').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // send mail listener
  document.querySelector("#compose-form").addEventListener("submit", function(event) {
    event.preventDefault();
    send_mail(this);
  });


});

function messageConstruct(message, type) {
  document.getElementById("message-alert-div").innerHTML = `
    <div class="alert alert-dismissible alert-${type} fade show" id="message-alert" role="alert">
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>
  `
}

function archiveButtonConstruct(mailId) {
  return `
    <button class="btn btn-danger" onclick='archiveMail(this)' data-mail-id="${mailId}" id="archive-button" style="align-self: flex-start">Archive</button> 
  `
}

function unarchiveButtonConstruct(mailId) {
  return `
    <button class="btn btn-warning" onclick='unarchiveMail(this)' data-mail-id="${mailId}" id="unarchive-button" style="align-self: flex-start">Unarchive</button> 
  `
}


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  document.querySelectorAll(".btn.btn-sm.btn-primary").forEach((button) => {
    button.classList.remove("btn-primary")
    button.classList.add("btn-outline-primary")
  })

  const composeButton = document.getElementById("compose")
  composeButton.classList.add("btn-primary")
  composeButton.classList.remove("btn-outline-primary")
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {
    const emailDiv = document.getElementById("emails-view")
    emails.forEach((email) => {

      let addOn = ""
      if (!email.read && mailbox !== "sent") {
        addOn = "font-weight: bold;"
      }
      else if (mailbox !== "sent") {
        addOn = "background-color: gainsboro;"
      }
      else {
        addOn = "background-color: aliceblue;"
      }

      emailDiv.insertAdjacentHTML( 'beforeend', `
        <div style="${addOn}" data-mail-id="${email.id}">
            <div style="width: 200px;overflow: hidden">${email.sender}</div>
            <div style="margin-right: auto">${email.subject}</div>
            <div>${email.timestamp}</div>
        </div>
      `)
    })
    Array.from(emailDiv.children).slice(1).forEach((div) => {
      div.addEventListener("click", () => {
        if (mailbox === "sent") {
          loadMail(div.dataset.mailId, true)
        }
        else {
          loadMail(div.dataset.mailId)
        }
      })
    })
  });

  const prevClickedButton = document.querySelector(".btn.btn-sm.btn-primary")
  if (prevClickedButton && prevClickedButton.getAttribute("id") !== mailbox.toLowerCase()) {
    prevClickedButton.classList.remove("btn-primary")
    prevClickedButton.classList.add("btn-outline-primary")
  }



  const clickedButton = document.getElementById(`${mailbox.toLowerCase()}`)
  clickedButton.classList.remove("btn-outline-primary")
  clickedButton.classList.add("btn-primary")
}


function send_mail(form) {
  const formData = new FormData(form);
  const to = formData.get("to");
  const subject = formData.get("subject");
  const body = formData.get("body");


  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: to,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.message) {
      messageConstruct(result.message, "success")
      form.reset()
      load_mailbox("sent")
    }
    else if (result.error) {
      messageConstruct(result.error, "danger")
      scroll({
        top: 0,
        left: 0,
        behavior: "smooth"
      })
    }
  })
}

function  loadMail(mailId, sentMail=false) {
  fetch(`/emails/${mailId}`)
  .then(response => response.json())
  .then(email => {
    if(email.error) {
      messageConstruct(email.error, "danger")
      scroll({
        top: 0,
        left: 0,
        behavior: "smooth"
      })
    }
    else {
      const headers = {
        "From": "sender",
        "To": "recipients",
        "Subject": "subject",
        "Timestamp": "timestamp"
      }
      let mailElement = ""

      if (!sentMail) {
        mailElement = `
        <div style="display: flex;justify-content: space-between;flex-direction: row-reverse;">
            <div>
                <button class="btn btn-primary" style="align-self: flex-start" data-mail-id="${email.id}" onclick="reply()">Reply</button>`
        if (email.archived) {
          mailElement += unarchiveButtonConstruct(email.id)
        }
        else
        {
          mailElement += archiveButtonConstruct(email.id)
        }
        mailElement += `</div><div>`
      }


      for (const header in headers) {
        mailElement += `
          <header>
            <h6 style="display: inline">${header}: </h6>
            <span>${email[headers[header]]}</span>
          </header>
        `;
      }
      if (!sentMail) {
       mailElement += `</div></div>`
      }
      mailElement += `
        <hr>
        <pre>${email.body}</pre>
      `

      document.getElementById("emails-view").innerHTML = mailElement

      mailStatus(mailId, "read", true)

    }
  });
}

function mailStatus(mailId, action, value) {
  return fetch(`/emails/${mailId}`, {
    method: 'PUT',
    body: JSON.stringify({
      [action]: value
    })
  })
}

function archiveMail(archiveBtn) {
  mailStatus(archiveBtn.dataset.mailId, "archived", true)
  .then(() => {
      messageConstruct("Message archived.", "info");
    })
  .then(() => {
    load_mailbox("inbox");
  })
}

function unarchiveMail(unarchiveBtn) {
  mailStatus(unarchiveBtn.dataset.mailId, "archived", false)
    .then(() => {
      messageConstruct("Message unarchived.", "info");
    })
    .then(() => {
      load_mailbox("inbox");
    })
}

function reply() {
  const to = document.querySelector("div header:first-child span").innerText
  const subject = document.querySelector("div header:nth-child(3) span").innerText
  const timestamp = document.querySelector("div header:nth-child(4) span").innerText
  const body = document.querySelector("#emails-view > pre").innerText

  const alreadyReplied = new RegExp('^On.*?wrote:.*?\n\n', 'm')

  const emailData = {
    to: to,
    subject: subject.startsWith("Re:") ? subject : "Re: " + subject,
    body: `On ${timestamp} ${to} wrote: ${body.replace(alreadyReplied, "")}\n\n`
  };

  compose_email()

  document.getElementById("compose-recipients").value = emailData.to
  document.getElementById("compose-subject").value = emailData.subject
  const bodyInput = document.getElementById("compose-body")
  bodyInput.value = emailData.body
  bodyInput.focus()



}