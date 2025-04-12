
  export function displayCombatResult(monster, data) {    
    const { xp, gold, drops, turns, monster_blocked_hits,
    player_blocked_hits, logs, result } = data.data.fight;
    
    if (result == 'win') {
      console.log(`Combat WON`)
      console.log(`${monster} was killed in ${turns} turns`)
      console.log(`${xp} xp won.`)
      console.log(`${drops.map(drop => console.log(`Looted ${drop.quantity} ${drop.code}`))} and ${gold} gold`)
      return;
    } else {
      console.log('**Combat LOST**')
      return;
    }
  }

  displayEndLog()