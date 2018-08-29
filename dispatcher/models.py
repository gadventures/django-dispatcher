from django.db import models


class MessageChain(models.Model):

    state = models.CharField(max_length=30)
    chain_type = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    date_next_update = models.DateField(auto_now=True)
    last_requested_by = models.CharField(max_length=30)
    disabled = models.NullBooleanField()

    def transition_to(self, new_state):
        self.state = new_state
        self.save()


class MessageChainEvent(models.Model):

    chain = models.ForeignKey(MessageChain, related_name='chain_event')
    date_created = models.DateField(auto_now_add=True)
    action = models.CharField(max_length=30)
    value = models.CharField(max_length=30)


class MessageChainResource(models.Model):

    chain = models.ForeignKey(MessageChain, related_name='chain_resources')
    resource_id = models.CharField(max_length=30)
    resource_type = models.CharField(max_length=30)
