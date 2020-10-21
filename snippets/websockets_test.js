#!/usr/bin/env node
const Web3 = require('web3');

const web3 = new Web3(new Web3.providers.WebsocketProvider('wss://eth-mainnet.ws.alchemyapi.io/v2/INFURATOKEN'));

const subscription = web3.eth.subscribe('newBlockHeaders', (error, blockHeader) => {
		if (error) return console.error(error);
		// console.log('Successfully subscribed!', blockHeader);
		const now = new Date(); 
		const blockTimestamp = JSON.parse(JSON.stringify(blockHeader)).timestamp;
		console.log("Time diff: ", now.getTime()/1000 - blockTimestamp);
		}).on('data', (blockHeader) => {
		// console.log('data: ', blockHeader);
		});
// unsubscribes the subscription
subscription.unsubscribe((error, success) => {
if (error) return console.error(error);

console.log('Successfully unsubscribed!');
});