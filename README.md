# Ethereum Fundraising Python Server

## Run

```
python assets/application.py
```

##Purchase steps

###At start of fundraiser
1. User sends value to intermediate Bitcoin address
2. Server sends from intermediate Bitcoin address with the following outputs
  * [0] Ethereum exodus address
  * [1] The hash160 that is your ethereum address
  * [2] The hash160 of your email address
3. Store users's email address along with its hash160 in mongodb

###2 months later:

1. Ethereum looks up your email address and sees if you got a reward
