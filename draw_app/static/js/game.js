'use strict';

import {canvas} from '../js/draw.js';
import {getResult} from '../js/response.js';
import {startScreen, endScreen} from '../js/screens.js';
import {createRandomWord} from '../js/words.js'


const checkButton = document.querySelector('.submit-draw-button');
const progressCounter = document.querySelector('.progress-bar-counter p');
const bestVariantScore = document.querySelector('.best-variant-count p');
const progressBar = document.querySelector('.progress-bar-slider');
const bestVariantShow = document.querySelector('.best-variant');
const checkResultShow = document.querySelector('.draw-check-result-wrapper');
const checkResultScore = document.querySelector('.draw-check-result p');


let bestScore = 0;
let bestVariant;
let onChecking = false;
let guessWord = createRandomWord();
console.log(guessWord);
const colorScheme = {
    0: 'linear-gradient(to right, #e5405e 0%, #ff8c00 100%)',
    20: 'linear-gradient(to right, #e5405e 0%, #ff8c00 50%, #ffdb3a 100%)',
    40: 'linear-gradient(to right, #e5405e 0%, #ff8c00 33%, #ffdb3a 66%, #ffff00 100%)',
    60: 'linear-gradient(to right, #e5405e 0%, #ff8c00 25%, #ffdb3a 50%, #ffff00 75%, #adff2f 100%)',
    80: 'linear-gradient(to right, #e5405e 0%, #ff8c00 20%, #ffdb3a 40%, #ffff00 60%, #adff2f 80%, #3fffa2 100%)',
}


function updateCounters() {
    progressCounter.innerHTML = bestScore + '%';
    bestVariantScore.innerHTML = bestScore + '%';
}

function updateBestShow(img) {
    bestVariant = 'url(' + img + ')';
    bestVariantShow.style.background = bestVariant;
    bestVariantShow.style.backgroundPosition = 'center';
    bestVariantShow.style.backgroundSize = 'cover';
}

function showResult(result, done) {
    if (done) {
        checkResultScore.innerHTML = 'Результат: ' + result + '%';
    } else {
        checkResultScore.innerHTML = 'Произошла ошибка!';
    }
    checkResultShow.style.display = 'flex';
    setTimeout(function() {
        checkResultShow.style.display = 'none';
    }, 2500);
}

function updateProgressBar(result) {
    let score = result / 100;
    progressBar.style.width = 'calc(100% * ' + score.toFixed(2) + ' - 20px)';

    if (result >= 80) {
        progressBar.style.background = colorScheme['80'];
    } else if (result >= 60) {
        progressBar.style.background = colorScheme['60'];
    } else if (result >= 40) {
        progressBar.style.background = colorScheme['40'];
    } else if (result >= 20) {
        progressBar.style.background = colorScheme['20'];
    } else {
        progressBar.style.background = colorScheme['0'];
    }
}

function processResult(result, img) {
    if (result['status'] == 'done') {
        result = result['result'];
        if (result >= 80) {
            result = 100;
        }
        showResult(result, true);
        if (result >= bestScore) {
            bestScore = result;
            updateBestShow(img);
            updateCounters();
            updateProgressBar(result);
        }
        if (result == 100) {
            setTimeout(function() {
                endScreen(guessWord['word'], bestVariant);
            }, 1000); 
        }
    } else {
        result = result['result'];
        showResult(result, false);
    }
}

checkButton.addEventListener('click', async function() {
    if (!onChecking) {
        onChecking = true;
        let img = canvas.toDataURL('image/png');
        let checkImg = img.replace(/^data:image\/(png|jpg);base64,/, '');
        let result = await getResult(checkImg, guessWord['index']);
        console.log(result);
        processResult(result, img);
        setTimeout(function() {
            onChecking = false;
        }, 2500);
    }
});

startScreen(guessWord['category']);
updateCounters();