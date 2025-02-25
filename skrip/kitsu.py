import os
import time
import random
from web3 import Web3
from colorama import Fore, Style, init

init(autoreset=True)

RPC_URL = "https://testnet-rpc.monorail.xyz"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx"
CONTRACT_ADDRESS = "0x2c9C959516e9AAEdB2C748224a41249202ca8BE7"
GAS_LIMIT_STAKE = 500000
GAS_LIMIT_UNSTAKE = 800000


def load_private_keys(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]


w3 = Web3(Web3.HTTPProvider(RPC_URL))
STAKE_AMOUNT = w3.to_wei(random.uniform(0.01, 0.1), 'ether')
UNSTAKE_DELAY = 5 * 60

# Send transaction
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


def stake_mon(wallet_address, private_key):
    print(f"{Fore.YELLOW}⚡ Staking {w3.from_wei(STAKE_AMOUNT, 'ether')} MON")
    data = "0xd5575982"  
    tx_hash = send_transaction(wallet_address, private_key, CONTRACT_ADDRESS, data, GAS_LIMIT_STAKE, STAKE_AMOUNT)
    print(f"{Fore.GREEN}✅ Stake transaction: {EXPLORER_URL}/{tx_hash}")
    return STAKE_AMOUNT

def unstake_gmon(wallet_address, private_key, amount):
    print(f"{Fore.MAGENTA}🔓 Unstaking {w3.from_wei(amount, 'ether')} gMON")
    function_selector = "0x6fed1ea7"
    padded_amount = w3.to_hex(amount)[2:].zfill(64)
    data = function_selector + padded_amount
    tx_hash = send_transaction(wallet_address, private_key, CONTRACT_ADDRESS, data, GAS_LIMIT_UNSTAKE)
    print(f"{Fore.GREEN}✅ Unstake transaction: {EXPLORER_URL}/{tx_hash}")

def run_auto_cycle(private_key, wallet_number):
    wallet_address = w3.eth.account.from_key(private_key).address
    try:
        stake_amount = stake_mon(wallet_address, private_key)
        print(f"{Fore.CYAN}⏳ [Wallet {wallet_number}] Waiting 5 minutes before unstaking...")
        time.sleep(UNSTAKE_DELAY)
        unstake_gmon(wallet_address, private_key, stake_amount)
    except Exception as e:
        print(f"{Fore.RED}❌ Error in Wallet {wallet_number}: {e}")

def main():
    private_keys = load_private_keys('pk.txt')
    print(f"{Fore.BLUE}🚀 Starting Kitsu Bot...")

    for i, private_key in enumerate(private_keys, start=1):
        wallet = w3.eth.account.from_key(private_key)
        print(f"{Fore.YELLOW}🌟 [Wallet {i}] Using account: {wallet.address}")
        run_auto_cycle(private_key, i)
        print(f"{Fore.GREEN}✅ [Wallet {i}] Cycle completed!\n")

    print(f"{Fore.MAGENTA}🎉 All cycles completed!")


if __name__ == "__main__":
    main()
