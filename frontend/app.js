let currentInput = "";
let isSessionActive = false;

const numberDisplay = document.getElementById('number-display');
const addNumber = document.getElementById('add-number');
const deleteBtn = document.getElementById('delete-btn');
const ussdOverlay = document.getElementById('ussd-overlay');
const ussdText = document.getElementById('ussd-text');
const ussdInput = document.getElementById('ussd-input');

// Show banner on load so the user understands what to do
window.addEventListener('load', () => {
    showPushNotification("🤖 NdalamaLite Demo", "Dial 888 and press Call to start the AI USSD simulation.");
});

function showPushNotification(title, message) {
    const banner = document.getElementById('ios-banner');
    document.querySelector('.banner-icon').innerText = title.includes("🤖") ? "🤖" : "💬";
    document.querySelector('.banner-title').innerText = title;
    document.querySelector('.banner-message').innerText = message;
    
    banner.classList.add('show');
    // Hide after 6 seconds
    setTimeout(() => {
        banner.classList.remove('show');
    }, 6000);
}

function updateDisplay() {
    numberDisplay.innerText = currentInput;
    
    // Mimic iOS resizing logic for long numbers
    if (currentInput.length > 10) {
        numberDisplay.style.fontSize = "32px";
    } else if (currentInput.length > 8) {
        numberDisplay.style.fontSize = "38px";
    } else {
        numberDisplay.style.fontSize = "44px";
    }

    if (currentInput.length > 0) {
        addNumber.style.visibility = "visible";
        deleteBtn.style.visibility = "visible";
    } else {
        addNumber.style.visibility = "hidden";
        deleteBtn.style.visibility = "hidden";
    }
}

function pressKey(key) {
    if (currentInput.length < 18) {
        currentInput += key;
        updateDisplay();
    }
}

function deleteKey() {
    currentInput = currentInput.slice(0, -1);
    updateDisplay();
}

async function makeCall() {
    if (currentInput === "888" || currentInput === "*888#" || currentInput.includes("123") || currentInput.includes("4705347734")) {
        isSessionActive = true;
        ussdOverlay.style.display = "flex";
        ussdText.innerText = "Please wait...";
        ussdInput.style.display = "none";
        
        await sendUSSDRequest("");
    } else {
        alert("Call Failed. Try dialing 888 for NdalamaLite.");
        currentInput = "";
        updateDisplay();
    }
}

async function sendUSSDRequest(payloadText) {
    ussdText.innerText = "Please wait...";
    try {
        const response = await fetch(`/ussd`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sessionId: "iphone-session-123",
                phoneNumber: "+260970000000",
                networkCode: "Airtel",
                serviceCode: "888",
                text: payloadText
            })
        });

        const data = await response.json();
        const ussdCommand = data.response;
        
        if (data.notification) {
            showPushNotification("Mobile Money", data.notification);
        }
        
        if (ussdCommand.startsWith("CON ")) {
            isSessionActive = true;
            ussdText.innerText = ussdCommand.replace("CON ", "");
            ussdInput.style.display = "block";
            ussdInput.value = "";
            ussdInput.focus();
            document.querySelector('.ussd-btn.reply').style.display = "block";
            document.querySelector('.ussd-btn.cancel').innerText = "Cancel";
        } else if (ussdCommand.startsWith("END ")) {
            isSessionActive = false;
            ussdText.innerText = ussdCommand.replace("END ", "");
            
            ussdInput.style.display = "none";
            document.querySelector('.ussd-btn.reply').style.display = "none";
            document.querySelector('.ussd-btn.cancel').innerText = "Dismiss";
        } else {
            ussdText.innerText = ussdCommand;
        }

    } catch (error) {
        console.error(error);
        ussdText.innerText = "Error performing request. Please ensure the backend server is running on port 8000 and is accessible on the LAN network.";
        isSessionActive = false;
        ussdInput.style.display = "none";
        document.querySelector('.ussd-btn.reply').style.display = "none";
        document.querySelector('.ussd-btn.cancel').innerText = "Dismiss";
    }
}

function cancelUSSD() {
    ussdOverlay.style.display = "none";
    isSessionActive = false;
    currentInput = "";
    updateDisplay();
}

function replyUSSD() {
    if (!isSessionActive) {
        cancelUSSD(); // dismiss
        return;
    }
    const val = ussdInput.value;
    sendUSSDRequest(val);
}

ussdInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        replyUSSD();
    }
});
