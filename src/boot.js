// boot.js
// exposes boot progress API for actual pyodide loading

const bootMessages = [
  {
    text: "BIOS Version 2.1.87 - Copyright (C) 1987 Iridescent Ivies",
    delay: 500,
    stage: "bios"
  },
  { text: "Memory Test: 640K OK", delay: 400, stage: "memory" },
  { text: "Extended Memory Test: 15360K OK", delay: 300, stage: "memory" },
  { text: "", delay: 200, stage: "memory" },
  { text: "Detecting Hardware...", delay: 400, stage: "hardware" },
  { text: "  - Primary Hard Disk.......... OK", delay: 300, stage: "hardware" },
  { text: "  - Network Interface.......... OK", delay: 300, stage: "hardware" },
  { text: "  - Math Coprocessor........... OK", delay: 200, stage: "hardware" },
  { text: "", delay: 200, stage: "hardware" },
  { text: "Loading SQL Social Network v1.0...", delay: 400, stage: "init" },
  { text: "Initializing Python Runtime Environment...", delay: 300, stage: "pyodide_start" },
  { text: "Loading Pyodide Kernel", delay: 0, showProgress: true, stage: "pyodide_load", waitForCallback: true },
  { text: "Installing setup scripts...", delay: 0, showProgress: true, stage: "setup_load", waitForCallback: true },
  { text: "Configuring Python modules...", delay: 0, showProgress: true, stage: "modules_load", waitForCallback: true },
  { text: "Loading parser and functions...", delay: 0, showProgress: true, stage: "functions_load", waitForCallback: true },
  { text: "Establishing database connections...", delay: 400, stage: "db_init" },
  { text: "Loading sample datasets...", delay: 300, stage: "data_init" },
  { text: "", delay: 200, stage: "complete" },
  { text: "System Ready!", delay: 300, blink: true, stage: "complete" },
  { text: "Press any key to continue...", delay: 500, blink: true, stage: "complete" },
];

let bootScreen = null;
let isBootComplete = false;
let continuePressed = false;
let currentMessageIndex = 0;
let bootContent = null;
let progressCallbacks = {};


window.bootProgress = {
  start: startBootSequence,
  pyodideLoaded: () => advanceToStage("setup_load"),
  setupLoaded: () => advanceToStage("modules_load"), 
  modulesLoaded: () => advanceToStage("functions_load"),
  functionsLoaded: () => advanceToStage("db_init"),
  complete: finishBoot,
  isComplete: () => isBootComplete,
  
  updateProgress: updateCurrentProgress,
  setProgressMessage: setProgressMessage
};

// update current progress bar to a specific percentage
function updateCurrentProgress(percentage) {
  const currentProgressBars = document.querySelectorAll('[id^="progress-bar-"]');
  const lastBar = currentProgressBars[currentProgressBars.length - 1];
  if (lastBar) {
    // clear any existing interval for this bar to prevent conflicts
    const barId = lastBar.id;
    if (progressCallbacks[barId]) {
      clearInterval(progressCallbacks[barId]);
      delete progressCallbacks[barId];
    }
    
    lastBar.style.width = Math.min(85, Math.max(0, percentage)) + "%";
  }
}

// add a custom progress message (optional)
function setProgressMessage(message) {
  const bootLines = bootContent.querySelectorAll('.boot-line');
  const lastLine = bootLines[bootLines.length - 1];
  if (lastLine && !lastLine.classList.contains('boot-blink')) {
    const progressDiv = lastLine.querySelector('.boot-progress');
    if (progressDiv) {
      lastLine.innerHTML = message + progressDiv.outerHTML;
    }
  }
}

async function startBootSequence() {
  continuePressed = false;
  currentMessageIndex = 0;

  bootScreen = document.createElement("div");
  bootScreen.className = "boot-screen";
  bootScreen.innerHTML = '<div class="boot-content" id="boot-content"></div>';

  document.body.appendChild(bootScreen);
  document.querySelector(".interface").style.opacity = "0";

  bootContent = document.getElementById("boot-content");

  // start showing messages up to first callback point
  await showMessagesUpToStage("pyodide_load");
  
  console.log("Boot sequence waiting for pyodide load...");
}

async function showMessagesUpToStage(targetStage) {
  while (currentMessageIndex < bootMessages.length) {
    if (continuePressed) {
      // fast-forward remaining messages
      showRemainingMessages();
      break;
    }

    const message = bootMessages[currentMessageIndex];
    
    // stop if we hit a callback stage that doesn't match the target
    if (message.waitForCallback && message.stage !== targetStage) {
      break;
    }

    await showMessage(message, currentMessageIndex);
    currentMessageIndex++;

    // if this was the target stage and it's a callback, stop here
    if (message.stage === targetStage && message.waitForCallback) {
      break;
    }
  }
}

async function advanceToStage(targetStage) {
  console.log(`Advancing boot to stage: ${targetStage}`);
  
  // complete current progress bar smoothly if there is one
  await completeCurrentProgressBar();
  
  // continue to next stage
  currentMessageIndex++;
  await showMessagesUpToStage(targetStage);
}

function completeCurrentProgressBar() {
  return new Promise((resolve) => {
    const currentProgressBars = document.querySelectorAll('[id^="progress-bar-"]');
    if (currentProgressBars.length === 0) {
      resolve();
      return;
    }

    let completed = 0;
    currentProgressBars.forEach(bar => {
      const barId = bar.id;
      
      if (progressCallbacks[barId]) {
        clearInterval(progressCallbacks[barId]);
        delete progressCallbacks[barId];
      }
      
      const currentWidth = parseFloat(bar.style.width) || 0;

      if (currentWidth >= 100) {
        completed++;
        if (completed === currentProgressBars.length) {
          resolve();
        }
        return;
      }
      
      const interval = setInterval(() => {
        const width = parseFloat(bar.style.width) || 0;
        if (width >= 100) {
          bar.style.width = "100%";
          clearInterval(interval);
          completed++;
          if (completed === currentProgressBars.length) {
            resolve();
          }
        } else {
          bar.style.width = Math.min(100, width + 12) + "%";
        }
      }, 30);
    });
  });
}

async function showMessage(message, index) {
  const line = document.createElement("div");
  line.className = "boot-line";

  if (message.showProgress) {
    line.innerHTML = message.text + 
      '<div class="boot-progress"><div class="boot-progress-bar" id="progress-bar-' + 
      index + '"></div></div>';
  } else {
    line.textContent = message.text;
  }

  if (message.blink) {
    line.classList.add("boot-blink");
  }

  bootContent.appendChild(line);

  setTimeout(() => {
    line.classList.add("boot-show");
  }, 50);

  if (message.showProgress && !message.waitForCallback) {
    await animateProgressBar("progress-bar-" + index);
  } else if (message.showProgress && message.waitForCallback) {
    startProgressBar("progress-bar-" + index);
  }

  if (message.delay > 0) {
    await new Promise(resolve => setTimeout(resolve, message.delay));
  }
}

function startProgressBar(barId) {
  const progressBar = document.getElementById(barId);
  if (!progressBar) return;

  // start at 0% and slowly increase until callback
  let progress = 0;
  progressBar.style.width = progress + "%";
  
  const interval = setInterval(() => {
    if (continuePressed) {
      progress = 100;
      progressBar.style.width = progress + "%";
      clearInterval(interval);
      return;
    }

    // slowly increase but never complete without callback
    // slow down as it gets closer to 90%
    const increment = progress < 50 ? Math.random() * 8 : Math.random() * 2;
    progress += increment;
    if (progress > 85) progress = 85;
    progressBar.style.width = progress + "%";
  }, 300);

  progressCallbacks[barId] = interval;
}

function animateProgressBar(barId) {
  return new Promise((resolve) => {
    const progressBar = document.getElementById(barId);
    if (!progressBar) {
      resolve();
      return;
    }

    let progress = 0;
    const interval = setInterval(() => {
      if (continuePressed) {
        progress = 100;
        clearInterval(interval);
        resolve();
        return;
      }

      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        resolve();
      }
      progressBar.style.width = progress + "%";
    }, 100);
  });
}

function showRemainingMessages() {
  const remainingMessages = bootMessages.slice(currentMessageIndex);
  remainingMessages.forEach((msg, i) => {
    const line = document.createElement("div");
    line.className = "boot-line boot-show";
    line.textContent = msg.text;
    if (msg.blink) line.classList.add("boot-blink");
    bootContent.appendChild(line);
  });
  currentMessageIndex = bootMessages.length;
}

async function finishBoot() {
  console.log("Finishing boot sequence...");

  // complete any remaining progress bars
  completeCurrentProgressBar();
  
  // show remaining messages
  currentMessageIndex++;
  await showMessagesUpToStage("complete");
  await waitForContinue();
  
  if (bootScreen) {
    bootScreen.style.opacity = "0";
    bootScreen.style.transition = "opacity 0.5s ease";

    setTimeout(() => {
      if (bootScreen && bootScreen.parentNode) {
        document.body.removeChild(bootScreen);
      }
      bootScreen = null;
    }, 500);
  }

  const mainInterface = document.querySelector(".interface");
  if (mainInterface) {
    mainInterface.style.transition = "opacity 0.5s ease";
    mainInterface.style.opacity = "1";
  }

  isBootComplete = true;
  console.log("Boot sequence complete - system ready");
}

function waitForContinue() {
  return new Promise((resolve) => {
    const handleInteraction = (e) => {
      e.preventDefault();
      e.stopPropagation();
      continuePressed = true;

      document.removeEventListener("keydown", handleInteraction, true);
      document.removeEventListener("click", handleInteraction, true);
      if (bootScreen) {
        bootScreen.removeEventListener("click", handleInteraction, true);
      }

      resolve();
    };

    document.addEventListener("keydown", handleInteraction, true);
    document.addEventListener("click", handleInteraction, true);
    if (bootScreen) {
      bootScreen.addEventListener("click", handleInteraction, true);
    }

    // Auto-continue after 3 seconds
    const timeoutId = setTimeout(() => {
      if (!continuePressed) {
        continuePressed = true;
        document.removeEventListener("keydown", handleInteraction, true);
        document.removeEventListener("click", handleInteraction, true);
        if (bootScreen) {
          bootScreen.removeEventListener("click", handleInteraction, true);
        }
        resolve();
      }
    }, 3000);

    const originalResolve = resolve;
    resolve = () => {
      clearTimeout(timeoutId);
      originalResolve();
    };
  });
}

// styles for boot screen (inject into document head)
const bootStyles = `
.boot-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  color: #00ff00;
  font-family: "JetBrains Mono", "Courier New", monospace;
  z-index: 10000;
  padding: 20px;
  font-size: 14px;
  line-height: 1.4;
  overflow-y: auto;
  cursor: pointer;
}

.boot-content {
  max-width: 800px;
  margin: 0 auto;
}

.boot-line {
  opacity: 0;
  margin-bottom: 2px;
  transition: opacity 0.3s ease;
}

.boot-line.boot-show {
  opacity: 1;
}

.boot-line.boot-blink {
  animation: bootBlink 0.5s infinite;
}

.boot-progress {
  display: inline-block;
  width: 200px;
  height: 8px;
  border: 1px solid #00ff00;
  margin-left: 10px;
  position: relative;
  vertical-align: middle;
}

.boot-progress-bar {
  height: 100%;
  background: #00ff00;
  width: 0%;
  transition: width 0.2s ease;
}

@keyframes bootBlink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
`;

const styleSheet = document.createElement("style");
styleSheet.textContent = bootStyles;
document.head.appendChild(styleSheet);
