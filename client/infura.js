const LendingPoolV2Artifact = require("@aave/protocol-v2/artifacts/contracts/protocol/lendingpool/LendingPool.sol/LendingPool.json");

const abi = require("./abi.js");
const chainlink = require("./chainlink.js");

// Log the ABI into console
//console.log(LendingPoolV2Artifact.abi);

const { ethers } = require("ethers");

const uniswap_anchored_view_address =
  "0x6D2299C48a8dD07a872FDd0F8233924872Ad1071";

const aave_lending_pool_v2_abi = LendingPoolV2Artifact.abi;
const aave_lending_pool_v2_address =
  "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9";

const aave_incentive_controller_address =
  "0xd784927Ff2f95ba542BfC824c8a8a98F3495f6b5";

const chainlink_aggregator_address =
  "0x37bC7498f4FF12C19678ee8fE19d713b87F6a9e6";

//const projectId = "fd3ac79f46ba4500be8e92da9632b476"; //Yonatan
const projectId = "474dfacad06547a4aba817b93fa852c9";

async function main() {
  const tstamp = () => new Date(Date.now()).toISOString();

  console.log("%s running infura client", tstamp());
  provider = ethers.providers.InfuraProvider.getWebSocketProvider(
    "homestead",
    projectId
  );

  block_number = await provider.getBlockNumber();
  console.log("%s connected to infura, last block %d", tstamp(), block_number);

  //
  //AAVE lending pool contract
  //
  const aave_lending_pool_contract = new ethers.Contract(
    aave_lending_pool_v2_address,
    aave_lending_pool_v2_abi,
    provider
  );

  /* await aave_lending_pool_contract.connect(provider);
     * aave_lending_pool_contract.on("Borrow", (...evt) => {
     *   console.log("%s lending pool borrow %s", tstamp(), evt);
     * });

     * aave_lending_pool_contract.on("Deposit", (...evt) => {
     *   console.log("%s lending pool deposit %s", tstamp(), evt);
     * }); */

  aave_lending_pool_contract.on("LiquidationCall", (...evt) => {
    console.log("%s lending pool liquidation  %s", tstamp(), evt);
    for (const _e of evt) {
      console.log("%s", _e);
    }
  });

  /* aave_lending_pool_contract.on("FlashLoan", (...evt) => {
   *   console.log("%s lending pool flashloan  %s", tstamp(), evt);
   *   for (const _e of evt) {
   *     console.log("%s", _e);
   *   }
   * }); */

  /* aave_lending_pool_contract.on("Repay", (...evt) => {
   *   console.log("%s lending pool repay  %s", tstamp(), evt);
   * }); */
  /*
   *   const evts = await aave_lending_pool_contract.queryFilter(
   *     "LiquidationCall",
   *     block_number - 1000
   *   );
   *   for (const evt of evts) {
   *     console.log("%s %s", tstamp(), evt);
   *   } */

  //
  //Price feed contract
  //
  const price_feed_contract = new ethers.Contract(
    uniswap_anchored_view_address,
    abi.uniswap_anchored_view_abi,
    provider
  );

  await price_feed_contract.connect(provider);

  const symbol_map = {};
  for (const symbol of [
    "ETH",
    "BTC",
    "DAI",
    "LINK",
    "USDT",
    "AAVE",
    "UNI",
    "YFI",
    "COMP",
    "MKR",
    "SUSHI",
    "USDC",
  ]) {
    if (1) {
      const config = await price_feed_contract.getTokenConfigBySymbol(symbol);
      symbol_map[config["symbolHash"]] = symbol;

      const price = await price_feed_contract.price(symbol);
      console.log("%s, %s price:", tstamp(), symbol, price.toNumber() / 1e6);
    }
  }

  console.log(symbol_map);

  //Query events in previous blocks
  /* const evts = await price_feed_contract.queryFilter(
   *   "PriceUpdated",
   *   13744592 - 50,
   *   13744592 + 2
   * );
   * for (const evt of evts) {
   *   console.log("%s %s", tstamp(), evt);
   *   console.log(
   *     "%s price %s %f",
   *     tstamp(),
   *     symbol_map[evt["topics"][0]],
   *     ethers.BigNumber.from(evt["data"]).toNumber() / 1e6
   *   );
   * } */

  //
  //Chainlink price oracles
  //
  const chainlink_oracles = {};
  for (const [contract, coin] of Object.entries(chainlink.price_oracles)) {
    const oracle = new ethers.Contract(contract, abi.chainlink_abi, provider);

    oracle.on("AnswerUpdated", (...evt) => {
      var price = evt[0];

      try {
        price = ethers.BigNumber.from(evt[0]).toNumber() / 1e8;
      } catch (error) {
        //console.log(error);
        //console.log(evt);
        price += "(failed conversion)";
      }

      console.log(
        "%s %s chainlink price update %s %f",
        tstamp(),
        evt[3]["blockNumber"],
        coin,
        price
      );
    });

    chainlink_oracles[coin] = oracle;

    console.log(
      "%s registering chainlink price oracle %s %s",
      tstamp(),
      coin,
      chainlink_oracles[coin].address
    );
  }

  const chainlink_eth_usd_contract = new ethers.Contract(
    chainlink_aggregator_address,
    abi.chainlink_abi,
    provider
  );

  //Query events in previous blocks
  /* const evts = await chainlink_eth_usd_contract.queryFilter(
   *   "AnswerUpdated",
   *   13744592 - 1000,
   *   13744592 + 2
   * );
   * for (const evt of evts) {
   *   //console.log("%s %s", tstamp(), evt);
   *   console.log(
   *     "%s %d chainlink eth/usd price %f",
   *     tstamp(),
   *     evt["blockNumber"],
   *     ethers.BigNumber.from(evt["topics"][1]).toNumber() / 1e6
   *   );
   * } */

  /* chainlink_eth_usd_contract.on("AnswerUpdated", (...evt) => {
   *   var price = ethers.BigNumber.from(evt[0]).toNumber() / 1e8;
   *   console.log(
   *     "%s %s chainlink price update (AnswerUpdated) %f",
   *     tstamp(),
   *     evt[3]["blockNumber"],
   *     price
   *   );
   *   for (const _e of evt) {
   *     console.log("%s", _e);
   *   }
   * }); */

  /* chainlink_eth_usd_contract.on("NewRound", (...evt) => {
   *   console.log("%s %s chainlink NewRound", tstamp(), evt[3]["blockNumber"]);
   * }); */

  price_feed_contract.on("PriceUpdated", (...evt) => {
    const symbol = symbol_map[evt[0]];
    if (typeof symbol !== "undefined") {
      console.log(
        "%s %d uniswap update  - price %s $%f",
        tstamp(),
        evt[2]["blockNumber"],
        symbol,
        evt[1].toNumber() / 1e6
      );
    }
  });

  //
  // Register for pending transactions
  //
  const monitor_pending_tx = false;
  if (monitor_pending_tx) {
    provider.on("pending", (tx) => {
      //console.log("%s pending tx: %s", tstamp(), tx);
      /* provider.getTransaction(tx).then(function (transaction) {
	 console.log(transaction); 
       *    }); */
    });
  }

  const monitor_blocks = false;
  if (monitor_blocks) {
    provider.on("block", (tx) => {
      console.log("%s block: %s", tstamp(), tx);
    });
  }

  //var prev_hfactor = 0.0;

  console.log("%s begin listening to live events", tstamp());

  while (true) {
    //Periodiclly track eth price via chainlink contract
    var eth_usd_price = await chainlink_eth_usd_contract.latestAnswer();
    eth_usd_price = eth_usd_price.toNumber() / 1e8;
    block_number = await provider.getBlockNumber();
    console.log(
      "%s %d chainlink query eth/usd price: %f",
      tstamp(),
      block_number,
      eth_usd_price
    );

    /* const tracked_account = "0xc65ee4f20226fF0f7AA546a368036E640c57D3BE";
       * const account_data = await aave_lending_pool_contract.getUserAccountData(
       *   tracked_account
       * );

       * var current_hfactor = account_data["healthFactor"] / 1e18;
       * console.log(
       *   "%s %s health factor: %s (%f)",
       *   tstamp(),
       *   tracked_account,
       *   current_hfactor,
       *   current_hfactor - prev_hfactor
	   * );
      

       * prev_hfactor = current_hfactor; */

    //Sleep for a while - listening to events in background
    const MIN = 60000;
    await new Promise((res) => setTimeout(() => res(null), 5 * MIN));
  }
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
