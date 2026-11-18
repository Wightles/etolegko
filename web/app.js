const REQUEST_COUNT = 10;
const CHUNK_SIZE = 64 * 1024;

const form = document.querySelector("#speed-form");
const urlInput = document.querySelector("#url-input");
const startButton = document.querySelector("#start-button");
const progressLabel = document.querySelector("#progress-label");
const progressBar = document.querySelector("#progress-bar");
const requestList = document.querySelector("#request-list");
const speedResult = document.querySelector("#speed-result");
const timeResult = document.querySelector("#time-result");
const sizeResult = document.querySelector("#size-result");

function formatMiB(bytes) {
  return (bytes / (1024 * 1024)).toFixed(2);
}

function formatSeconds(seconds) {
  return seconds.toFixed(3);
}

function createRequestItems() {
  requestList.innerHTML = "";
  for (let index = 1; index <= REQUEST_COUNT; index += 1) {
    const item = document.createElement("div");
    item.className = "request-item";
    item.id = `request-${index}`;
    item.innerHTML = `<span>${index}</span><strong>—</strong>`;
    requestList.append(item);
  }
}

function setRequestState(index, state, detail) {
  const item = document.querySelector(`#request-${index}`);
  if (!item) return;
  item.className = `request-item ${state}`;
  item.querySelector("strong").textContent = detail;
}

function resetResults() {
  speedResult.textContent = "0.00";
  timeResult.textContent = "0.000";
  sizeResult.textContent = "0.00";
}

async function downloadOnce(url) {
  const startedAt = performance.now();
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Сервер вернул HTTP ${response.status}`);
  }

  if (!response.body) {
    throw new Error("Браузер не дал доступ к телу ответа");
  }

  const reader = response.body.getReader();
  let downloadedBytes = 0;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    downloadedBytes += value.byteLength;
  }

  return {
    bytes: downloadedBytes,
    seconds: (performance.now() - startedAt) / 1000,
  };
}

async function runTest(url) {
  let totalBytes = 0;
  let totalSeconds = 0;

  for (let index = 1; index <= REQUEST_COUNT; index += 1) {
    setRequestState(index, "active", "загрузка");
    const result = await downloadOnce(url);
    totalBytes += result.bytes;
    totalSeconds += result.seconds;
    setRequestState(index, "done", `${formatSeconds(result.seconds)} с`);
    progressBar.style.width = `${(index / REQUEST_COUNT) * 100}%`;
    progressLabel.textContent = `${index}/${REQUEST_COUNT}`;
  }

  speedResult.textContent = formatMiB(totalBytes / totalSeconds);
  timeResult.textContent = formatSeconds(totalSeconds / REQUEST_COUNT);
  sizeResult.textContent = formatMiB(totalBytes);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const url = urlInput.value.trim();

  try {
    const parsedUrl = new URL(url);
    if (!["http:", "https:"].includes(parsedUrl.protocol)) {
      throw new Error("Используйте URL с http:// или https://");
    }

    createRequestItems();
    resetResults();
    progressBar.style.width = "0%";
    progressLabel.textContent = `0/${REQUEST_COUNT}`;
    startButton.disabled = true;
    startButton.textContent = "...";

    await runTest(url);
  } catch (error) {
    progressLabel.textContent = "Ошибка";
    const activeItem = document.querySelector(".request-item.active");
    if (activeItem) {
      activeItem.className = "request-item error";
      activeItem.querySelector("strong").textContent = "ошибка";
    }
    window.alert(`Не удалось выполнить запрос. ${error.message}`);
  } finally {
    startButton.disabled = false;
    startButton.textContent = "Проверить";
  }
});

createRequestItems();
