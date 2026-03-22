function hsLeaderElection(n: number) {
  // 1. Generate UNIQUE UIDs (shuffle)
  const uids = Array.from({ length: n }, (_, i) => i + 1).sort(
    () => Math.random() - 0.5,
  );

  const processes = uids.map((uid) => ({
    uid,
    active: true,
  }));

  // Fast lookup: uid → index
  const uidToIndex = new Map<number, number>();
  processes.forEach((p, i) => uidToIndex.set(p.uid, i));

  let totalMessages = 0;
  let rounds = 0;

  const mod = (x: number) => (x + n) % n;

  for (let phase = 0; ; phase++) {
    const distance = 2 ** phase;
    rounds++;

    let messages: any[] = [];

    // 1. Send OUT messages
    for (let i = 0; i < n; i++) {
      if (!processes[i].active) continue;

      messages.push({
        uid: processes[i].uid,
        sender: i, // track original sender
        origin: i,
        dir: -1,
        hopsLeft: distance,
        type: "OUT",
      });

      messages.push({
        uid: processes[i].uid,
        sender: i,
        origin: i,
        dir: 1,
        hopsLeft: distance,
        type: "OUT",
      });

      totalMessages += 2;
    }

    const replies = new Map<number, number>(); // index → IN count

    while (messages.length > 0) {
      const newMessages: any[] = [];

      for (const msg of messages) {
        const nextIndex = mod(msg.origin + msg.dir);
        msg.origin = nextIndex;

        if (msg.type === "OUT") {
          if (processes[nextIndex].uid > msg.uid) {
            processes[msg.sender].active = false;
            continue;
          }

          if (msg.hopsLeft > 1) {
            msg.hopsLeft--;
            newMessages.push(msg);
            totalMessages++;
          } else {
            // turn into IN message
            newMessages.push({
              uid: msg.uid,
              sender: msg.sender,
              origin: nextIndex,
              dir: -msg.dir,
              type: "IN",
            });
            totalMessages++;
          }
        } else {
          // IN message
          const homeIndex = uidToIndex.get(msg.uid)!;

          if (nextIndex === homeIndex) {
            const count = replies.get(homeIndex) || 0;
            replies.set(homeIndex, count + 1);

            // received both directions
            if (count + 1 === 2) {
              // Leader condition
              if (distance >= n) {
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
const result = hsLeaderElection(10);

console.log("Leader UID:", result.leader);
console.log("Rounds:", result.rounds);
console.log("Total messages:", result.totalMessages);
