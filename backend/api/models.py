from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Editing the already present abstract user class"""
    pass


class Club(models.Model):
    """"Model for clubs"""
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    requests = models.ManyToManyField('User', through='ClubMembershipRequest')

    def __str__(self):
        """"The name of each instance is the name of the club"""
        return self.name


class ClubMembershipRequest(models.Model):
    """Model to club requests"""
    STATUS_CHOICES = (
        ('PD', 'Pending'),
        ('AC', 'Accepted'),
        ('RE', 'Rejected'),
        ('CN', 'Cancelled'),
    )

    """ when a user/club is deleted, all references to the user/club is deleted as well.
    each request will have a user (who sent the request) and a club(to which they sent the request)"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)

    """Timestap to when the request of sent, automaticaly sets the time when created"""

    initiated = models.DateTimeField(auto_now_add=True, blank=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, blank=False, default='PD')

    """Timestap to when it was addressed"""

    closed = models.DateTimeField(default=None, blank=True, null=True)


class ClubRole(models.Model):

    """Model to provide club roles to users"""

    PRIVILEGE_CHOICES = (
        ('REP', 'Representative'),
        ('MEM', 'Member')
    )
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()

    """ Each clubrole would belong to a specific club"""

    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False, related_name='roles')

    """ Club Roles and Users have a many-many relationship with ClubMembership as an intermediate.
    This helps to filter the PRIVILEGE_CHOICES  """

    members = models.ManyToManyField('User', through='ClubMembership')
    privilege = models.CharField(max_length=3, choices=PRIVILEGE_CHOICES, blank=False, default='MEM')

    def __str__(self):
        return str(self.club) + " " + str(self.name)


class ClubMembership(models.Model):

    """Model to represent a relation between user and their club role"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    club_role = models.ForeignKey('ClubRole', on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Project(models.Model):

    """Model for projects assossiated with a club"""

    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    started = models.DateTimeField(auto_now_add=True, blank=False)
    closed = models.DateTimeField(default=None, blank=True, null=True)

    """ The deletion of leader does not result in deletion of the Project """

    leader = models.ForeignKey('User', on_delete=models.PROTECT, blank=False, related_name='lead_projects')

    members = models.ManyToManyField('User', through='ProjectMembership')
    clubs = models.ManyToManyField('Club', through='ClubProject')

    def __str__(self):
        return str(self.name)


class ClubProject(models.Model):
    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=False)


class ProjectMembership(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Channel(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField()

    """Each club would have only one channel, if the club is deleted, the channel also would be deleted """

    club = models.OneToOneField('Club', on_delete=models.CASCADE, blank=False)

    """A many-many relationship between channel and users.
    The relationship is connected through an intermediate channel subscribers so as to filter them out. """

    subscribers = models.ManyToManyField('User', through='ChannelSubscription')

    def __str__(self):
        return str(self.club) + " " + str(self.name)


class ChannelSubscription(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)

    """On deleting a channel, the subscription field gets deleted as well """

    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, blank=False)
    joined = models.DateTimeField(auto_now_add=True, blank=False)


class Post(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    """ Each post would belong to a channel, if the channel is deleted, all posts belonging to the channel will be deleted  """
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.channel) + " " + str(self.created)


class Conversation(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)

    """Each conversation takes place in a channel """

    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, blank=False)
    author = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)

    """ Each child conversation would be related to a parent conversations"""
    """If the parent conversation is deleted, the child conversations would also be deleted """

    parent = models.ForeignKey('Conversation', on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.channel) + " " + str(self.created)


class Feedback(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)

    """Feedback for a club """

    club = models.ForeignKey('Club', on_delete=models.CASCADE, blank=False)
    author = models.ForeignKey('User', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.club) + " " + str(self.created)


class FeedbackReply(models.Model):
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    parent = models.OneToOneField('Feedback', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.parent) + " " + str(self.created)
