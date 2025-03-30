let data = await fetch('data/data.json').then(response => response.json());

export function createRandomWord() {
    let randomIndex = Math.floor(Math.random() * data.length);
    return data[randomIndex];
}