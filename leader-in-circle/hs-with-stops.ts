import readline from "readline";

function waitForEnter(): Promise<void> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question("➡️ Press Enter for next step...", () => {
      rl.close();
      resolve();
    });
  });
}

async function hsStepSimulator(n: number) {
  const uids = Array.from({ length: n }, (_, i) => i + 1).sort(
    () => Math.random() - 0.5,
  );

  const processes = uids.map((uid) => ({
    uid,
    active: true,
  }));

  const uidToIndex = new Map<number, number>();
  processes.forEach((p, i) => uidToIndex.set(p.uid, i));

  const mod = (x: number) => (x + n) % n;

  let totalMessages = 0;
  let rounds = 0;

  console.log("\n🌐 Initial Ring:");
  console.log(uids.map((u, i) => `[${i}:${u}]`).join(" → "));
  console.log("====================================");

  for (let phase = 0; ; phase++) {
    const distance = 2 ** phase;
    rounds++;

    console.log(`\n🔥 Phase ${phase} (distance = ${distance})`);

    let messages: any[] = [];

    for (let i = 0; i < n; i++) {
      if (!processes[i].active) continue;

      const uid = processes[i].uid;

      messages.push({
        uid,
        sender: i,
        origin: i,
        dir: -1,
        hopsLeft: distance,
        type: "OUT",
      });
      messages.push({
        uid,
        sender: i,
        origin: i,
        dir: 1,
        hopsLeft: distance,
        type: "OUT",
      });

      console.log(`➡️ ${uid} sends OUT`);
      totalMessages += 2;
    }

    const replies = new Map<number, number>();
    let step = 0;

    while (messages.length > 0) {
      step++;

      console.log(`\n--- Step ${step} ---`);
      await waitForEnter();

      const newMessages: any[] = [];

      for (const msg of messages) {
        const from = msg.origin;
        const to = mod(from + msg.dir);

        console.log(`📨 ${msg.type} UID=${msg.uid} : ${from} → ${to}`);

        msg.origin = to;

        if (msg.type === "OUT") {
          if (processes[to].uid > msg.uid) {
            console.log(`💥 ${msg.uid} killed by ${processes[to].uid}`);
            processes[msg.sender].active = false;
            continue;
          }

          if (msg.hopsLeft > 1) {
            msg.hopsLeft--;
            newMessages.push(msg);
            totalMessages++;
          } else {
            console.log(`🔁 ${msg.uid} turns to IN`);
            newMessages.push({
              uid: msg.uid,
              sender: msg.sender,
              origin: to,
              dir: -msg.dir,
              type: "IN",
            });
            totalMessages++;
          }
        } else {
          const home = uidToIndex.get(msg.uid)!;

          if (to === home) {
            const count = replies.get(home) || 0;
            replies.set(home, count + 1);

            console.log(`📥 ${msg.uid} got IN (${count + 1}/2)`);

            if (count + 1 === 2) {
              console.log(`✅ ${msg.uid} survives phase ${phase}`);

              if (distance >= n) {
                console.log(`\n🏆 LEADER ELECTED: ${msg.uid}`);
                console.log("====================================");

                return {
                  leader: msg.uid,
                  rounds,
                  totalMessages,
                };
              }
            }
          } else {
            newMessages.push(msg);
            totalMessages++;
          }
        }
      }

      messages = newMessages;
    }
  }
}

// 🔥 Run
(async () => {
  const result = await hsStepSimulator(5);

  console.log("\nFinal Result:");
  console.log("Leader:", result.leader);
  console.log("Rounds:", result.rounds);
  console.log("Messages:", result.totalMessages);
})();
