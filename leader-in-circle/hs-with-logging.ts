function hsLeaderElectionWithTrace(n: number) {
  const uids = Array.from({ length: n }, (_, i) => i + 1).sort(
    () => Math.random() - 0.5,
  );

  const processes = uids.map((uid) => ({
    uid,
    active: true,
  }));

  const uidToIndex = new Map<number, number>();
  processes.forEach((p, i) => uidToIndex.set(p.uid, i));

  let totalMessages = 0;
  let rounds = 0;

  const mod = (x: number) => (x + n) % n;

  console.log("Initial ring:");
  console.log(uids.map((u, i) => `[${i}:${u}]`).join(" → "));
  console.log("--------------------------------------------------");

  for (let phase = 0; ; phase++) {
    const distance = 2 ** phase;
    rounds++;

    console.log(`\n🔥 Phase ${phase} (distance = ${distance})`);

    const activeList = processes
      .map((p, i) => (p.active ? `${p.uid}@${i}` : null))
      .filter(Boolean);

    console.log("Active:", activeList.join(", "));

    let messages: any[] = [];

    // OUT messages
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

      console.log(`➡️ ${uid} sends OUT both directions`);
      totalMessages += 2;
    }

    const replies = new Map<number, number>();

    let step = 0;

    while (messages.length > 0) {
      step++;
      console.log(`\n--- Step ${step} ---`);

      const newMessages: any[] = [];

      for (const msg of messages) {
        const from = msg.origin;
        const to = mod(from + msg.dir);

        console.log(`📨 ${msg.type} msg UID=${msg.uid} moves ${from} → ${to}`);

        msg.origin = to;

        if (msg.type === "OUT") {
          if (processes[to].uid > msg.uid) {
            console.log(
              `💥 UID ${msg.uid} killed by stronger UID ${processes[to].uid} at ${to}`,
            );
            processes[msg.sender].active = false;
            continue;
          }

          if (msg.hopsLeft > 1) {
            msg.hopsLeft--;
            newMessages.push(msg);
            totalMessages++;
          } else {
            console.log(
              `🔁 UID ${msg.uid} reached max distance → returning IN`,
            );
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
          const homeIndex = uidToIndex.get(msg.uid)!;

          if (to === homeIndex) {
            const count = replies.get(homeIndex) || 0;
            replies.set(homeIndex, count + 1);

            console.log(`📥 UID ${msg.uid} received IN (${count + 1}/2)`);

            if (count + 1 === 2) {
              console.log(`✅ UID ${msg.uid} survived phase ${phase}`);

              if (distance >= n) {
                console.log(`🏆 LEADER ELECTED: ${msg.uid}`);
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

// 🔥 Run it
const result_n2 = hsLeaderElectionWithTrace(5);

console.log("\n==============================");
console.log("Leader UID:", result_n2.leader);
console.log("Rounds:", result_n2.rounds);
console.log("Total messages:", result_n2.totalMessages);
