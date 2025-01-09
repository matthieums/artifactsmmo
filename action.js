
import { moveTo, fight, gather, rest, craft, deposit, withdraw } from "./api.js";
import { setCurrentPosition, setCurrentLevels } from "./state.js";


const commands = {
  move: moveTo,
  fight: fight,
  rest: rest,
  gather: gather,
  craft: craft,
  deposit: deposit,
  withdraw: withdraw
}

async function main() {

  try {
    await setCurrentPosition();
    await setCurrentLevels();
    handleCommandLineArgs();
  } catch(error) {
    console.log('error', error);
  }
}

async function handleCommandLineArgs() {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('wrong command line argument. Usage: node file.js action args');
    return;
  }

  const action = args[0];
  const params = args.slice(1);
  const command = commands[action];

  if (command) {
    try {
      await command(...params);
      } catch(error) {
        console.log('error:', error);
      }
  } else {
    console.log(`Unknown command: ${action}. Usage: node file.js <action> [args...]`)
  }
}

main();