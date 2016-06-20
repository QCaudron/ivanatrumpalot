![Make America Hate Again](https://github.com/QCaudron/ivanatrumpalot/blob/master/images/banner.jpg)


Ivana Trumpalot
===============

*A deep learning bot trained on the crap coming out of Donald Trump's mouth.*


Twitter
-------

[@IvanaTrumpalot](https://twitter.com/IvanaTrumpalot) tweets once an hour. She will answer your tweets directed at her. She also answers the tweets of [@BernieSanders](https://twitter.com/berniesanders), [@HillaryClinton](https://twitter.com/hillaryclinton), [@BarackObama](https://twitter.com/barackobama), and [@WhiteHouse](https://twitter.com/whitehouse), hopefully with a witty, on-topic slice of Trumpian wisdom. Got a target in mind ? Let us know by opening up an issue.


Network
-------

Ivana Trumpalot is a recurrent neural network using the Long Short-Term Memory paradigm. The code is written in Keras, and is fully available in this repository.


Data
----

We downloaded a handful of Trump's speeches, purged them for special characters we didn't want to keep, and removed any audience participation that was transcribed the the speeches. The corpus currently consists of about 250,000 characters, or 46,000 words. This corpus is also available in this repo.


Usage
-----

**Training** : To train the model, simply call `code/train_lstm.py`. Feel free to change the parameters and architecture of the network, as well as the dataset you use. The network will be saved to disk every five epochs. On a GTX 980 Ti, it takes about three minutes per epoch.

**Predictions** : Using the `predict()` function in `code/ivanatrumpalot.py`, feed it some text and it will generate some output for you.

**Twitter** : If you want to set up a Twitter bot, we use [this package](https://github.com/sixohsix/twitter). Don't forget to feed your API keys to `code/twitter_bot.py`.


The Name
--------

Ivana Trumpalot is, of course, a reference to the antagonist in *Austin Powers 2 : The Spy Who Shagged Me*. She's groovy, baby. Ivana Trump is also Donald Trump's wife. This isn't a personal attack at her; you must understand, the name was simply too great to pass up. We have the best names. The best names.


The Authors
-----------

[Mike](https://github.com/sempwn) and [Quentin](http://quentincaudron.com) are as interested in deep learning and neural nets as Trump is interested in building big walls. They did their PhDs at the University of Warwick, and are both currently working in Vancouver, BC.
