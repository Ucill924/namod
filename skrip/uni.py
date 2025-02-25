import os
import time
import random
from web3 import Web3
from web3.middleware import geth_poa_middleware
from colorama import Fore, Style
from sympy import symbols

CHAIN_ID = 10143
UNISWAP_V2_ROUTER_ADDRESS = Web3.to_checksum_address("0xCa810D095e90Daae6e867c19DF6D9A8C56db2c89")
WETH_ADDRESS = Web3.to_checksum_address("0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701")

erc20_abi = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
]

uniswap_v2_router_abi = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": ["uint256[]"],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETH",
        "outputs": ["uint256[]"],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

TOKEN_ADDRESSES = {
    "DAC": Web3.to_checksum_address("0x0f0bdebf0f83cd1ee3974779bcb7315f9808c714"),
    "USDT": Web3.to_checksum_address("0x88b8e2161dedc77ef4ab7585569d2415a1c1055d"),
    "WETH": Web3.to_checksum_address("0x836047a99e11f376522b447bffb6e3495dd0637c"),
    "MUK": Web3.to_checksum_address("0x989d38aeed8408452f0273c7d4a17fef20878e62"),
    "USDC": Web3.to_checksum_address("0xf817257fed379853cDe0fa4F97AB987181B1E5Ea"),
    "CHOG": Web3.to_checksum_address("0xE0590015A873bF326bd645c3E1266d4db41C4E6B")
}

def load_private_keys(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def connect_to_rpc():
    rpc_urls = [
        "https://testnet-rpc.monorail.xyz",
        "https://testnet-rpc.monad.xyz",
        "https://monad-testnet.drpc.org"
    ]
    
    for url in rpc_urls:
        web3 = Web3(Web3.HTTPProvider(url))
        if web3.is_connected():
            print(Fore.GREEN + f"✅ Connected to {url}" + Style.RESET_ALL)
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            return web3
    raise ValueError(Fore.RED + "❌ Unable to connect to any RPC" + Style.RESET_ALL)

def sleep(ms):
    time.sleep(ms / 1000)

def get_random_eth_amount():
    return Web3.to_wei(random.uniform(0.0001, 0.01), 'ether')

def swap_eth_for_tokens(web3, wallet, token_address, amount_in_wei, token_symbol):
    router_contract = web3.eth.contract(address=UNISWAP_V2_ROUTER_ADDRESS, abi=uniswap_v2_router_abi)
    nonce = web3.eth.get_transaction_count(wallet.address)
    
    try:
        print(Fore.YELLOW + f"🔄 Swapping {Web3.from_wei(amount_in_wei, 'ether')} Monad for {token_symbol}" + Style.RESET_ALL)
        tx = router_contract.functions.swapExactETHForTokens(
            0,
            [WETH_ADDRESS, token_address],
            wallet.address,
            int(time.time()) + 60 * 10
        ).build_transaction({
            'chainId': CHAIN_ID,
            'gas': 200000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
            'value': amount_in_wei
        })

        signed_tx = web3.eth.account.sign_transaction(tx, wallet.key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(Fore.CYAN + f"🚀 Transaction hash: {tx_hash.hex()}" + Style.RESET_ALL)

        web3.eth.wait_for_transaction_receipt(tx_hash)
        print(Fore.GREEN + "✅ Transaction confirmed!" + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"❌ Failed to swap: {e}" + Style.RESET_ALL)

def main():
    private_keys = load_private_keys('pk.txt')
    web3 = connect_to_rpc()
    
    for i, private_key in enumerate(private_keys, start=1):
        wallet = web3.eth.account.from_key(private_key)
        print(Fore.MAGENTA + f"[Wallet {i}] Using account: {wallet.address}" + Style.RESET_ALL)
        
        for token_symbol, token_address in TOKEN_ADDRESSES.items():
            eth_amount = get_random_eth_amount()
            swap_eth_for_tokens(web3, wallet, token_address, eth_amount, token_symbol)
            print(Fore.BLUE + "⏳ Random time sleep\n" + Style.RESET_ALL)
            time.sleep(random.randint(8, 15))
            
if __name__ == "__main__":
    main()
