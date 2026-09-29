/* =========================
   ELEMENTS
========================= */

const textInput =
    document.getElementById("textInput");

const charCount =
    document.getElementById("charCount");

const pace =
    document.getElementById("pace");

const paceValue =
    document.getElementById("paceValue");

const voiceSelect =
    document.getElementById("voice");

const voicePreview =
    document.getElementById("voicePreview");

const voicePreviewPlayer =
    document.getElementById("voicePreviewPlayer");

const generateBtn =
    document.getElementById("generateBtn");

const loading =
    document.getElementById("loading");

const audioBox =
    document.getElementById("audioBox");

const audioPlayer =
    document.getElementById("audioPlayer");

const downloadBtn =
    document.getElementById("downloadBtn");

const emptyMessage =
    document.getElementById("emptyMessage");


/* =========================
   CHARACTER COUNTER
========================= */

textInput.addEventListener(
    "input",
    function () {

        charCount.textContent =
            this.value.length;

    }
);


/* =========================
   PACE
========================= */

pace.addEventListener(
    "input",
    function () {

        paceValue.textContent =
            parseFloat(this.value).toFixed(2);

    }
);


/* =========================
   VOICE SELECTION
========================= */

voiceSelect.addEventListener(
    "change",
    function () {

        const selectedOption =
            this.options[this.selectedIndex];


        /*
         * Nothing selected
         */

        if (!this.value) {

            voicePreview.style.display =
                "none";

            voicePreviewPlayer.pause();

            voicePreviewPlayer.removeAttribute(
                "src"
            );

            return;
        }


        /*
         * Get reference audio URL
         */

        const previewUrl =
            selectedOption.dataset.previewUrl;


        if (!previewUrl) {

            voicePreview.style.display =
                "none";

            return;
        }


        /*
         * Set preview audio
         */

        voicePreviewPlayer.src =
            previewUrl;

        voicePreviewPlayer.load();


        /*
         * Show preview player
         */

        voicePreview.style.display =
            "block";

    }
);


/* =========================
   GENERATE AUDIO
========================= */

generateBtn.addEventListener(
    "click",
    function () {

        const text =
            textInput.value.trim();

        const voice =
            voiceSelect.value;

        const model =
            document.getElementById(
                "model"
            ).value;

        const language =
            document.getElementById(
                "language"
            ).value;

        const seed =
            document.getElementById(
                "seed"
            ).value;

        const paceValueNumber =
            parseFloat(pace.value);


        /*
         * Text validation
         */

        if (!text) {

            alert(
                "Please enter some text."
            );

            return;
        }


        /*
         * Voice validation
         */

        if (!voice) {

            alert(
                "Please select a voice."
            );

            return;
        }


        /*
         * Temporary loading
         */

        generateBtn.disabled =
            true;

        generateBtn.textContent =
            "Generating...";

        loading.classList.add(
            "active"
        );


        /*
         * Temporary data
         *
         * Later this will be sent
         * to Django using fetch().
         */

        console.log({
            text: text,
            voice: voice,
            model: model,
            language: language,
            seed: seed,
            pace: paceValueNumber
        });


        /*
         * Temporary simulation
         */

        setTimeout(
            function () {

                generateBtn.disabled =
                    false;

                generateBtn.textContent =
                    "🎙 Generate Audio";

                loading.classList.remove(
                    "active"
                );

                alert(
                    "TTS backend is not connected yet."
                );

            },
            500
        );

    }
);