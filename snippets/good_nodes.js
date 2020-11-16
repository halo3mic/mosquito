var enodeTable = document.getElementsByClassName("table")[0]
var enodeList = []
var info = []
var commandList = []
var commandStart = 'curl --data \'{"jsonrpc":"2.0","method":"parity_addReservedPeer","params":["';
var commandEnd = '"],"id":0}\' -H "Content-Type: application/json" -X POST localhost:8545'


for (i = 1; i < enodeTable.rows.length; i++) {
    var enodeUrl = "";
    var command= "";
    // GET THE CELLS COLLECTION OF THE CURRENT ROW.
    var objCells = enodeTable.rows.item(i).cells;
    var btn = objCells[8]
    copySpan = btn.getElementsByClassName("d-none")
    enodeUrl = copySpan[0].innerText
    enodeList.push(enodeUrl);
    command = commandStart + enodeUrl + commandEnd;
    commandList.push(command);
}
var arrLength = commandList.length
for(i=0; i< arrLength; i++)
{
    console.log(commandList[i]);
}