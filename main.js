
import readline from 'node:readline';
import { stdin as input, stdout as output } from 'node:process';
import { commands } from './commands.js';
import { fetchState } from './state.js';

export const rl = readline.createInterface({ input, output, prompt: '> ' });

  async function main() {
  try {
    console.log('Loading...')
    await fetchState();
  } catch(error) {
    console.log('error', error);
  }

  console.log('Welcome to the game! Type a command to start.');
  rl.prompt();

  rl.on('line', async (line) => {
    await handleCommand(line);
    rl.prompt();
  });

  rl.on('close', () => {
    console.log('Script end');
    process.exit(0);
  });
}

async function handleCommand(input) {
  const [action, ...params] = input.trim().split(' ');
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