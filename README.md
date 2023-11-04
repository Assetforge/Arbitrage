# Risk Management to do's

#Global variables referenced before assignement
#Find a way to close the position because of the fees the buy quantity is too high to close
# -> Define criteria and conditions when and how to exit the trade -> Take a look at security issues concerning API Keys
# -> Define a size limit on transaction -> Number of active position equal to one at first -> Arbitrage of one asset at first

#An error occurred: APIError(code=-1013): Filter failure: LOT_SIZE
# Find a way to close the right quantity of the position
# Every symbol traded on Binance has a specific LOT_SIZE filter that defines the rules for the allowed order quantity. These rules include the minimum quantity, maximum quantity, and step size (the increment the quantity can be increased by).
#
# Here's what each of these terms means:
#
# Minimum Quantity: The smallest amount of the asset that you can order.
# Maximum Quantity: The largest single order of the asset that you can place.
# Step Size: The minimum increment by which your order quantity can increase or decrease.
# To resolve this issue, you need to ensure that the quantity you're specifying in your order adheres to the symbol's LOT_SIZE filter. You can retrieve these details by using the Binance API's exchangeInfo endpoint, which provides trading rules and symbol information. You would need to adjust your order quantity to match these constraints.
#
# Here's how you could get the LOT_SIZE filter details for a specific symbol and adjust your order quantity accordingly:


#Position partielle si jamais l'opportunité d'arbitrage ne se résorbe pas et s'agrandit
#Augmenter ou diminuer le prix d'achat moyen. Et tirer profit d'un écart plus important des prix
#
# IMPROVE SPEED do access to the API as few as possible

#RISK MANAGEMENT

