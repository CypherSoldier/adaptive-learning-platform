function smallestMult(n) {
  let maximum = n;

  let m = 999999999;
  console.log('Max', maximum)

  while (maximum < m) {
    let count = 0;

    for (let i = 1; i <= n; i++) {
      if (maximum % i === 0) count++;
    }

    if (count === n) {
      if (maximum < m) {
        m = maximum;
      }
    }

    maximum++;
  }

  return m;
}

let tests = [5, 7, 10, 13, 20];

for (let test of tests) {
  console.log(smallestMult(test));
}