# django-dispatcher


Logic engine for determining order of things to execute


Sometimes there's a series of things that must run in sequence. This is a
configuration based approach enabling that.


Typical Usage
---


1. Create some transition objects. They are basically Interfaces that
require some methods and properties to be defined and reward you with
some context built at an appropriate time.

The required functions/params include:

- final_state (String)
- is_valid (Function returning Boolean)
- context (Function returning Dict)

```python

from dispatcher import Transition


class Cart2DayReminder(Transition):

    final_state = CART_2_DAY_REMINDER_SENT

    @property
    def onlinebooking(self):
        return OnlineBooking.objects.get(pk=self.resources['online_booking'])

    def is_valid(self):

        if self.onlinebooking.date_updated < (datetime.now() - timedelta(days=2)):
            self.errors.append('The booking was created less than 2 days ago')
            return False

        return True

    def build_context(self):
        return {
            'booking': self.onlinebooking.to_dict(),
        }


class Cart1WeekReminder(Transition):
    ...


```

2. Create a config, listing the transitions that can happen. When a chain state is found, it can transition to the listed transitions. After that is done, the chain moves to a new state. The next time this runs, it'll find the new state and try to transition to the new transitions.

```python
DISPATCHER_CONFIG = {
    'chains': [
        {
            'chain_type': 'abandoned_cart',
            'transitions': {
                NEW: [Cart2DayReminder, Cart1WeekReminder],
                Cart2DayReminder.final_state: [Cart1WeekReminder, ],
                Cart1WeekReminder.final_state: [],
            }
        }
    ]
}

```


3. Initialize the dispatcher with the above settings. You'll have to
determine the `chain_type` on your own. Its name must be the same as
the above config.


```python

from dispatcher import Dispatcher

dispatcher = Dispatcher(DISPATCHER_CONFIG)

```

4. Provide the resources to query searching for a chain. The chain
will query using an `AND` statement, meaning all the resources must
be present when retrieving the chain.

```python

chain = dispatcher.get_or_create_chain(
    chain_type='chain_type',
    rsc_mappings=[
        ('online_booking', '123456'),
        ('customer', '57844')
    ]
)

```

5. Provide a callback for the chain. Should a chain transition to a new
valid state, whatever callback you pass will be sent on. The callback
takes the transition passed in and any callback arguments specified.

```python

def some_callback(transition, **callback_args):
    # so something magical
    # the transition will contain a `transition.build_context`, which will
    # return the stuff to pass to the callback


chain.execute(callback=some_callback, callback_args={})

```
