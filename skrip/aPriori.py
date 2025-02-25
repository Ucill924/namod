import os
import random
import time
import requests
from web3 import Web3
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

RPC_URL = "https://testnet-rpc.monad.xyz"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"
CONTRACT_ADDRESS = "0xb2f82D0f38dc453D596Ad40A37799446Cc89274A"
GAS_LIMIT_STAKE = 500000
GAS_LIMIT_UNSTAKE = 800000
GAS_LIMIT_CLAIM = 800000

with open('pk.txt', 'r') as file:
    PRIVATE_KEYS = [line.strip() for line in file.readlines()]

w3 = Web3(Web3.HTTPProvider(RPC_URL))

minimal_abi = [
    {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "getPendingUnstakeRequests", "outputs": [{"name": "", "type": "uint256[]"}], "type": "function"}
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=minimal_abi)

def get_random_amount():
    min_amount = 0.01
    max_amount = 0.05
    random_amount = random.uniform(min_amount, max_amount)
    return w3.to_wei(round(random_amount, 4), 'ether')

def get_random_delay():
    return random.randint(60, 120)

def send_transaction(wallet_address, private_key, to, data, gas_limit, value=0):
    try:
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
    except Exception as e:
        print(Fore.RED + f"❌ Transaction failed: {e}")
        return None

def stake_mon(wallet_address, private_key):
    stake_amount = get_random_amount()
    print(Fore.CYAN + f"🌿 [{wallet_address}] Staking {w3.from_wei(stake_amount, 'ether')} MON")

    data = ("0x6e553f65" +
            w3.to_hex(stake_amount)[2:].zfill(64) +
            wallet_address[2:].zfill(64))

    tx_hash = send_transaction(wallet_address, private_key, CONTRACT_ADDRESS, data, GAS_LIMIT_STAKE, stake_amount)
    if tx_hash:
        print(Fore.YELLOW + f"🔗 Stake transaction hash: {tx_hash}")
    return stake_amount

def request_unstake(wallet_address, private_key, amount):
    data = ("0x7d41c86e" +
            w3.to_hex(amount)[2:].zfill(64) +
            wallet_address[2:].zfill(64) * 2)

    tx_hash = send_transaction(wallet_address, private_key, CONTRACT_ADDRESS, data, GAS_LIMIT_UNSTAKE)
    if tx_hash:
        print(Fore.MAGENTA + f"📉 [{wallet_address}] Unstaking {w3.from_wei(amount, 'ether')} MON\n")
def check_claimable_status(wallet_address):
    print(Fore.LIGHTBLUE_EX + f"🔍 Checking claimable status for {wallet_address}...")
    url = f"https://testnet.monadexplorer.com/api/v1/unstake-requests?address={wallet_address}"
    response = requests.get(url).json()
    claimable = next((req for req in response if not req['claimed'] and req['is_claimable']), None)
    return claimable['id'] if claimable else None

def claim_mon(wallet_address, private_key):
    claim_id = check_claimable_status(wallet_address)
    if not claim_id:
        print(Fore.RED + f"🚫 [{wallet_address}] No claimable withdrawals found.")
        return

    print(Fore.GREEN + f"💸 [{wallet_address}] Claiming withdrawal ID: {claim_id}")
    data = ("0x492e47d2" +
            "0000000000000000000000000000000000000000000000000000000000000040" +
            wallet_address[2:].zfill(64) +
            "0000000000000000000000000000000000000000000000000000000000000001" +
            w3.to_hex(claim_id)[2:].zfill(64))

    tx_hash = send_transaction(wallet_address, private_key, CONTRACT_ADDRESS, data, GAS_LIMIT_CLAIM)
    if tx_hash:
        print(Fore.YELLOW + f"🔗 Claim transaction hash: {tx_hash}")

def run_cycle(private_key):
    wallet_address = w3.eth.account.from_key(private_key).address
    try:
        print(Fore.BLUE + f"🚀 Processing wallet: {wallet_address}")
        stake_amount = stake_mon(wallet_address, private_key)
        time.sleep(15)
        request_unstake(wallet_address, private_key, stake_amount)
        print(Fore.GREEN + f"✨ Menungu req unstake  {wallet_address} 11 menit\n")
        time.sleep(660)
        claim_mon(wallet_address, private_key)
        print(Fore.GREEN + f"✅ Cycle completed for {wallet_address}\n")
    except Exception as e:
        print(Fore.RED + f"❌ [{wallet_address}] Cycle failed: {e}")

def main():
    print(Fore.MAGENTA + "🔥 Starting aPriori... 🔥")
    for index, private_key in enumerate(PRIVATE_KEYS, start=1):
        wallet_address = w3.eth.account.from_key(private_key).address
        print(Fore.YELLOW + f"🔢 [{index}] Using wallet: {wallet_address}")
        run_cycle(private_key)
        print(Fore.CYAN + "✨ Cycle finished ✨\n")
    print(Fore.GREEN + "🎯 All cycles completed successfully! 🎯")

if __name__ == "__main__":
    main()
