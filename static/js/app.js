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


// =====================================================
// CHARACTER COUNT
// =====================================================

textInput.addEventListener(
    "input",
    function () {

        charCount.textContent =
            this.value.length;

    }
);


// =====================================================
// PACE
// =====================================================

pace.addEventListener(
    "input",
    function () {

        paceValue.textContent =
            parseFloat(
                this.value
            ).toFixed(2);

    }
);


// =====================================================
// VOICE PREVIEW
// =====================================================

voiceSelect.addEventListener(
    "change",
    function () {

        const selectedOption =
            this.options[
                this.selectedIndex
            ];


        if (!this.value) {

            voicePreview.style.display =
                "none";

            voicePreviewPlayer.pause();

            voicePreviewPlayer.removeAttribute(
                "src"
            );

            return;
        }


        const previewUrl =
            selectedOption.dataset.previewUrl;


        if (!previewUrl) {

            voicePreview.style.display =
                "none";

            return;
        }


        voicePreviewPlayer.src =
            previewUrl;

        voicePreviewPlayer.load();

        voicePreview.style.display =
            "block";

    }
);


// =====================================================
// CSRF
// =====================================================

function getCSRFToken() {

    const csrfInput =
        document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );


    if (!csrfInput) {
        return "";
    }


    return csrfInput.value;
}


// =====================================================
// GENERATE
// =====================================================

generateBtn.addEventListener(
    "click",
    async function () {


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


        const cfgWeight =
            parseFloat(
                pace.value
            );


        // =========================================
        // VALIDATION
        // =========================================

        if (!text) {

            alert(
                "Please enter some text."
            );

            return;
        }


        if (text.length > 30000) {

            alert(
                "Maximum 30,000 characters allowed."
            );

            return;
        }


        if (!voice) {

            alert(
                "Please select a voice."
            );

            return;
        }


        // =========================================
        // UI
        // =========================================

        generateBtn.disabled = true;

        generateBtn.textContent =
            "Generating...";

        loading.classList.add(
            "active"
        );


        try {


            // =====================================
            // FORM DATA
            // =====================================

            const formData =
                new FormData();


            formData.append(
                "text",
                text
            );


            formData.append(
                "voice",
                voice
            );


            formData.append(
                "model",
                model
            );


            formData.append(
                "language",
                language
            );


            formData.append(
                "seed",
                seed
            );


            formData.append(
                "pace",
                cfgWeight
            );


            // =====================================
            // REQUEST
            // =====================================

            const response =
                await fetch(
                    generateBtn.dataset.url,
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken":
                                getCSRFToken()
                        },

                        body: formData
                    }
                );


            const data =
                await response.json();


            // =====================================
            // ERROR
            // =====================================

            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.error ||
                    "Generation failed."
                );

            }


            // =====================================
            // AUDIO
            // =====================================

            audioPlayer.src =
                data.audio_url;

            audioPlayer.load();


            downloadBtn.href =
                data.audio_url;


            downloadBtn.download =
                data.filename;


            emptyMessage.style.display =
                "none";


            audioBox.style.display =
                "flex";


            // =====================================
            // AUTOPLAY
            // =====================================

            try {

                await audioPlayer.play();

            } catch (error) {

                console.log(
                    "Autoplay blocked."
                );

            }


        } catch (error) {

            console.error(
                "Generation error:",
                error
            );


            alert(
                "Generation failed:\n\n" +
                error.message
            );


        } finally {

            generateBtn.disabled =
                false;


            generateBtn.textContent =
                "🎙 Generate Audio";


            loading.classList.remove(
                "active"
            );

        }

    }
);