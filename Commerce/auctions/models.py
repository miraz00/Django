from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class User(AbstractUser):
    pass


class AuctionListings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winning_bids", null=True, blank=True)
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=5000, null=True, blank=True)
    starting_bid = models.FloatField(default=0, validators=[MinValueValidator(0)])
    current_bid = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    category = models.CharField(max_length=64, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    watchlisted_by = models.ManyToManyField(User, related_name="watchlists", blank=True)

    def save(self, *args, **kwargs):
        if self.category:
            self.category = self.category.capitalize()
        if self.current_bid:
            if self.current_bid < self.starting_bid:
                raise ValidationError("Current bid must be greater than or equal to the starting bid")
        self.title = self.title
        self.starting_bid = round(self.starting_bid, 2)
        super(AuctionListings, self).save(*args, **kwargs)

    def __str__(self):
        if self.active:
            if self.bidder:
                return f"{self.title} from {self.user.username}: Current bid:{self.current_bid} by {self.bidder.username}"
            return f"{self.title} from {self.user.username}: No bids yet."
        else:
            if self.bidder:
                return f"{self.title} from {self.user.username}: won by {self.bidder.username} for {self.current_bid}"
            return f"{self.title} from {self.user.username}: closed without any buyer"

    class Meta:
        verbose_name_plural = 'Auction listings'


class Bids(models.Model):
    item = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="bids", )
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", )
    amount = models.FloatField(validators=[MinValueValidator(0)])
    datetime = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.item.current_bid:
            if self.amount <= self.item.current_bid:
                raise ValidationError("Bid amount must be greater than the current bid.")
        else:
            if self.amount < self.item.starting_bid:
                raise ValidationError("Bid amount must be at least the starting bid.")

        self.item.current_bid = self.amount
        self.item.bidder = self.bidder
        self.item.save()
        super(Bids, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.title} bid for {self.amount} by {self.bidder}"

    class Meta:
        verbose_name_plural = 'Bids'


class Comments(models.Model):
    item = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="comments", )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", )
    comment = models.CharField(max_length=2048)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.item.title}: {self.comment}"

    class Meta:
        verbose_name_plural = 'Comments'
