import os
import random
import time
from web3 import Web3
from colorama import Fore, Style, init


init(autoreset=True)


RPC_URL = "https://testnet-rpc.monorail.xyz"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx"
CONTRACT_ADDRESS = "0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701"
GAS_LIMIT_WRAP = 500000
GAS_LIMIT_UNWRAP = 500000


with open('pk.txt', 'r') as file:
    PRIVATE_KEYS = [line.strip() for line in file.readlines()]


w3 = Web3(Web3.HTTPProvider(RPC_URL))


minimal_abi = [
    {"constant": False, "inputs": [], "name": "deposit", "outputs": [], "type": "function"},
    {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], "name": "withdraw", "outputs": [], "type": "function"}
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=minimal_abi)

def get_random_amount():
    min_amount = 0.01
    max_amount = 0.05
    random_amount = random.uniform(min_amount, max_amount)
    return w3.to_wei(round(random_amount, 4), 'ether')

def get_random_delay():
    return random.randint(60 * 1000, 3 * 60 * 1000)

def send_transaction(wallet_address, private_key, to, data, gas_limit, value=0):
    tx = {
        'to': to,
        'data': data,
        'gas': gas_limit,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(wallet_address),
        'value': value
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def wrap_mon(wallet_address, private_key):
    amount = get_random_amount()
    print(Fore.CYAN + f"🚀 Wrapping {w3.from_wei(amount, 'ether')} MON > WMON for wallet: {wallet_address}")

    data = "0xd0e30db0"  
    tx_hash = send_transaction(wallet_address, private_key, CONTRACT_ADDRESS, data, GAS_LIMIT_WRAP, amount)
    print(Fore.MAGENTA + f"✅ Wrap transaction hash: {EXPLORER_URL}/{tx_hash}\n")

def unwrap_mon(wallet_address, private_key, amount):
    print(Fore.YELLOW + f"🔓 Unwrapping {w3.from_wei(amount, 'ether')} WMON > MON for wallet: {wallet_address}")

    data = "0x2e1a7d4d" + w3.to_hex(amount)[2:].zfill(64)  # withdraw(amount)
    tx_hash = send_transaction(wallet_address, private_key, CONTRACT_ADDRESS, data, GAS_LIMIT_UNWRAP)
    print(Fore.MAGENTA + f"✅ Unwrap transaction hash: {EXPLORER_URL}/{tx_hash}\n")

def run_swap_cycle(private_key, cycles=1):
    wallet_address = w3.eth.account.from_key(private_key).address
    print(Fore.BLUE + f"💸 Starting swap cycle for wallet: {wallet_address}")
    try:
        for i in range(1, cycles + 1):
            print(Fore.GREEN + f"🔥 Cycle {i} for wallet: {wallet_address}")
            amount = get_random_amount()
            wrap_mon(wallet_address, private_key)
            time.sleep(8)
            unwrap_mon(wallet_address, private_key, amount)
            print(Fore.YELLOW + f"⏳ Waiting 8 seconds before next step...")
            time.sleep(4)
        print(Fore.GREEN + f"✅ Swap cycle completed for wallet: {wallet_address}\n")
    except Exception as e:
        print(Fore.RED + f"❌ Error in run_swap_cycle for wallet {wallet_address}: {e}\n")

def main():
    print(Fore.CYAN + "✨ Starting wrap-unwrap ✨")
    for idx, private_key in enumerate(PRIVATE_KEYS, start=1):
        print(Fore.BLUE + f"🔢 Processing Wallet #{idx}")
        run_swap_cycle(private_key)
    print(Fore.CYAN + "🎉 All swaps completed! 🎉")

if __name__ == "__main__":
    main()
