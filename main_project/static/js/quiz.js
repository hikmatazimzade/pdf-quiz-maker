let timer;
let totalSeconds = 0;
const questions = quizDataFromServer;
const shown = showNumber;

const questionElement = document.getElementById('question');
const answerButtons = document.getElementById('answer-buttons');
const nextButton = document.getElementById('next-question');
const backButton = document.getElementById('back-to-quiz');

let currentQuestionIndex = 0;
let score = 0;
let userAnswers = [];

function startTimer() {
    timer = setInterval(setTime, 1000);
}

function stopTimer() {
    clearInterval(timer);
}

function setTime() {
    ++totalSeconds;
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds - hours * 3600) / 60);
    const seconds = totalSeconds - (hours * 3600 + minutes * 60);

    document.getElementById("timer").innerHTML = pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);
}

function pad(val) {
    const valString = val + "";
    if (valString.length < 2) {
        return "0" + valString;
    } else {
        return valString;
    }
}

function startQuiz() {
    totalSeconds = 0;
    startTimer();
    currentQuestionIndex = 0;
    score = 0;
    userAnswers = [];
    nextButton.innerHTML = gettext("Next");
    backButton.style.display = 'none';
    showQuestion();
}

function showQuestion() {
    resetState();
    let currentQuestion = questions[currentQuestionIndex];
    if (shown === true) {
        let question_no = currentQuestionIndex + 1;
        questionElement.innerHTML = question_no + ". " + currentQuestion.question;
    } else {
        questionElement.innerHTML = currentQuestion.question;
    }

    currentQuestion.answers.forEach((answer, index) => {
        const button = document.createElement("button");
        button.innerHTML = answer;
        button.classList.add("ans");
        if (index === currentQuestion.correctAnswer) {
            button.dataset.correct = true;
        }

        answerButtons.appendChild(button);
        button.addEventListener("click", selectAnswer);
    });
}

function resetState() {
    nextButton.style.display = "none";
    while (answerButtons.firstChild) {
        answerButtons.removeChild(answerButtons.firstChild);
    }
}

function selectAnswer(e) {
    const selectedAns = e.target;
    const isCorrect = selectedAns.dataset.correct === "true";
    if (isCorrect) {
        selectedAns.classList.add("correct");
        score++;
    } else {
        selectedAns.classList.add("incorrect");
    }
    Array.from(answerButtons.children).forEach(button => {
        if (button.dataset.correct === "true") {
            button.classList.add("correct");
        }
        button.disabled = true;
    });

    userAnswers[currentQuestionIndex] = {
        question: questions[currentQuestionIndex].question,
        selectedAnswer: selectedAns.textContent,
        correctAnswer: questions[currentQuestionIndex].answers[questions[currentQuestionIndex].correctAnswer]
    };

    if (currentQuestionIndex === questions.length - 1) {
        nextButton.innerHTML = gettext("Complete Quiz!");
    }

    nextButton.style.display = 'block';
}

function showScore() {
    stopTimer();
    resetState();
    var translatedText = gettext('Your score:');
    questionElement.innerHTML = `${translatedText} ${score} / ${questions.length}`;
    userAnswers.forEach((item, index) => {
        if (item.selectedAnswer !== item.correctAnswer) {
            const questionDiv = document.createElement("div");
            questionDiv.classList.add("review-question");

            var translate_question = gettext('Question');
            var translate_answer = gettext('Correct answer:');
            var your_answer_translate = gettext('Your answer:');

            questionDiv.innerHTML = `<strong>${translate_question} ${index + 1}:</strong> ${item.question}<br>
                                     <strong>${your_answer_translate}</strong> <span class="incorrect">${item.selectedAnswer}</span><br>
                                     <strong>${translate_answer}</strong> ${item.correctAnswer}`;
            answerButtons.appendChild(questionDiv);
        }
    });
    nextButton.innerHTML = gettext("Start Quiz Again");
    nextButton.style.display = 'block';
    backButton.style.display = 'block';
}

function handleNextButton() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        showQuestion();
    } else {
        showScore();
    }
}

nextButton.addEventListener("click", () => {
    if (currentQuestionIndex < questions.length) {
        handleNextButton();
    } else {
        startQuiz();
    }
});

startQuiz();