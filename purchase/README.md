# ethereum purchase dev

## steps

1. display a page with user address input and submit button
  1. submitting the form first validates then stores the user address
  1. application exhibits "processing" status to user
1. server contacts payment processor to generate a new deposit address
  1. despoit address is stored with a reference to the user address
  1. deposit address is displayed to the user
  1. application exhibits that it is waiting for user payment
1. user submits payment to deposit address
  1. payment processor notifies application that payment was received
  1. application records payment amount and reference
  1. application displays confirmation to user

## needs
* purchase
 * welcome/input user address
 * payment request w/qr code
 * transaction complete
* view
 * input user address/display message/verify signature
 * view purchases

## model

* user
 * user_id (i.e. bitcoin_address)
 * created_date
 * payments[]
* payment
 * reference_code
 * deposit_address
 * amount_satoshis
 * payment_timestamp

