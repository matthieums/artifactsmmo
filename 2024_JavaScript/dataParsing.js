let TOTALLOOT = {
    xp: 0,
    gold: 0,
    drops: []
}


export function (xp, gold, drops) {
    let currentLoot = {
        xp: 0,
        gold: 0,
        drops: []
    }

    // Log xp gained from action
    if (xp) {
        currentLoot.xp = xp
        TOTALLOOT.xp += parseInt(xp)
        console.log(`Total xp gained: \n ${xp}`)
    }


    // Log items looted
    if (Object.keys(loot).length > 0) {
        console.log('Loot collected:')
        for (const [item, quantity] of Object.entries(loot)) {
            console.log(` ${item}: ${quantity} \n`);
        }
    }
}

    // Log levels gained
    if (Object.keys(levels).length > 0) {
        console.log("Levels gained:");
        for (const [stat, level] of Object.entries(levels)) {
            console.log(` ${stat}: ${level} \n`);
        }
    }

export function logAllLoot() {
    console.log(TOTALLOOT);
    return;
}