'use strict';

const gameField = document.querySelector('.game-field');

export function startScreen(category) {
    const background = document.createElement('div');
    const startScreen = document.createElement('div');
    const logoImg = document.createElement('img');
    const welcomeText = document.createElement('p');
    const startButton = document.createElement('div');
    const startButtonText = document.createElement('p');

    background.className = 'menu-background';
    startScreen.className = 'start-screen';
    logoImg.className = 'logo-img';
    welcomeText.className = 'welcome-text';
    startButton.className = 'start-button';

    logoImg.src = 'img/logo.svg';
    logoImg.alt = 'logo';
    welcomeText.innerHTML = 'Привет! Сыграем в Doodler? Мы загадали некоторое слово из категории <b>' + category + '</b>. <br>Твоя цель — не только угадать его, но и нарисовать. Удачи!</p>';
    startButtonText.innerHTML = 'Играть!';

    startButton.appendChild(startButtonText);
    startScreen.appendChild(logoImg);
    startScreen.appendChild(welcomeText);
    startScreen.appendChild(startButton);
    background.appendChild(startScreen);

    gameField.appendChild(background);

    startButton.onclick = function() {
        background.classList.add('start-screen-disappear');
        setTimeout(function() {
            background.remove();
        }, 1400);
    }
}

export function endScreen(guessedWord, bestVariant) {
    const background = document.createElement('div');
    const endScreen = document.createElement('div');
    const bestVariantWin = document.createElement('div');
    const bestVariantTitle = document.createElement('div');
    const bestVariantTitleText = document.createElement('p');
    const winCongrats = document.createElement('div');
    const winCongratsPart1 = document.createElement('p');
    const winCongratsPart2 = document.createElement('p');
    const replayButton = document.createElement('a');
    const replayButtonText = document.createElement('p');

    background.className = 'menu-background';
    background.classList.add('end-screen-appear');
    endScreen.className = 'end-screen';
    bestVariantWin.className = 'best-variant-win';
    bestVariantTitle.className = 'best-variant-title';
    winCongrats.className = 'win-congrats';
    replayButton.className = 'replay-button'

    bestVariantWin.style.background = bestVariant;
    bestVariantTitleText.innerHTML = 'Это твой лучший рисунок!';
    winCongratsPart1.innerHTML = '<p>Ты победил(-а)! Поздравляем! Мы и правда загадали слово <b>' + guessedWord + '</b>.</p>';
    winCongratsPart2.innerHTML = 'Понравилось? Сыграй еще раз!';
    replayButton.href = '/';
    replayButtonText.innerHTML = 'Играть снова!';

    bestVariantTitle.appendChild(bestVariantTitleText);
    bestVariantWin.appendChild(bestVariantTitle);
    replayButton.appendChild(replayButtonText);
    winCongrats.appendChild(winCongratsPart1);
    winCongrats.appendChild(winCongratsPart2);
    winCongrats.appendChild(replayButton);
    endScreen.appendChild(bestVariantWin);
    endScreen.appendChild(winCongrats);
    background.append(endScreen);

    gameField.appendChild(background);
}