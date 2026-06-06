(function () {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";

  const I18N = {
    en: {
      "nav.doctor": "Doctor Console",
      "nav.parent": "Parent Portal",
      "nav.logout": "Sign Out",
      "nav.signIn": "Sign In",
      "home.kicker": "Pediatric AI post-visit care workspace",
      "home.copy": "Turn pediatric visit conversations into clear summaries, parent education, child-friendly guidance, and shareable follow-up documents.",
      "home.tryDemo": "Try Demo",
      "home.note1": "OpenPediCare supports post-visit communication and does not replace clinical judgment.",
      "home.note2": "Inspired by the PostVisit-style capture, context assembly, and multi-audience output pattern.",
      "login.title": "Sign in to your workspace",
      "login.copy": "Demo accounts can enter the full clinic and parent flows. Replace passwords and fill `.env` secrets before production.",
      "login.account": "Account",
      "login.password": "Password",
      "login.demoDoctor": "Demo doctor",
      "login.demoParent": "Demo parent",
      "doctor.title": "Realtime pediatric visit",
      "doctor.subtitle": "Enter the child's basic details, record the visit, review the read-only live transcript, optionally add notes, and generate clear post-visit education.",
      "doctor.metricPatients": "Patients",
      "doctor.metricAnalyses": "Analyses",
      "doctor.metricSpeech": "Speech",
      "doctor.tabVisit": "Visit",
      "doctor.tabHistory": "Recent Analyses",
      "doctor.flowPatient": "Patient",
      "doctor.flowPatientSmall": "Name, age, sex",
      "doctor.flowRecord": "Record",
      "doctor.flowRecordSmall": "Speech to transcript",
      "doctor.flowNote": "Notes",
      "doctor.flowNoteSmall": "Skip or add context",
      "doctor.flowResult": "Analysis",
      "doctor.flowResultSmall": "Summary and education",
      "doctor.patientTitle": "Child basics",
      "doctor.patientName": "Name",
      "doctor.patientNamePlaceholder": "Demo Child",
      "doctor.patientAge": "Age",
      "doctor.patientSex": "Sex",
      "doctor.createAndRecord": "Create case and start recording",
      "doctor.returningTitle": "Returning patient",
      "doctor.returningCopy": "Use this for follow-up visits so the History tab can stay focused on completed analyses.",
      "doctor.returningPlaceholder": "Choose an existing child",
      "doctor.startFollowUp": "Start follow-up visit",
      "doctor.currentPatient": "Current case",
      "doctor.recordTitle": "Recording and live transcript",
      "doctor.recordReadyTitle": "Ready to record",
      "doctor.recordReadyHelp": "Chrome and Edge can show a read-only live transcript. Each sentence is placed on a new line.",
      "doctor.startRecording": "Start recording",
      "doctor.pause": "Pause",
      "doctor.resume": "Resume",
      "doctor.stopRecording": "Stop recording",
      "doctor.transcript": "Live transcript",
      "doctor.transcriptPlaceholder": "The read-only transcript appears here sentence by sentence after recording starts.",
      "doctor.noteTitle": "Add physician notes?",
      "doctor.noteCopy": "After stopping the recording, you can add key instructions, medication wording, follow-up timing, or family questions. You can also skip this step.",
      "doctor.notesLabel": "Physician notes",
      "doctor.notesPlaceholder": "Example: Return urgently if breathing worsens, lethargy appears, or urine output drops.",
      "doctor.skipAnalyze": "Skip and analyze",
      "doctor.addAnalyze": "Add notes and analyze",
      "doctor.outputTitle": "Analysis result",
      "doctor.summaryTab": "Visit summary",
      "doctor.parentTab": "Parent education",
      "doctor.patientTab": "Patient education",
      "doctor.outputEmpty": "After recording and notes are complete, the analysis result will appear here.",
      "doctor.parentLink": "Parent view link",
      "doctor.recentTitle": "Recent analyses",
      "doctor.notReady": "Not generated yet",
      "doctor.noAnalyses": "No analyses yet.",
      "doctor.viewResult": "View",
      "status.idle": "Ready",
      "status.waiting": "Waiting",
      "status.socketReady": "Recording channel ready",
      "status.recording": "Recording",
      "status.paused": "Paused",
      "status.notes": "Waiting for notes",
      "status.processing": "Analyzing",
      "status.done": "Complete",
      "status.failed": "Failed",
      "status.disconnected": "Disconnected",
      "gender.female": "Female",
      "gender.male": "Male",
      "gender.other": "Other",
      "gender.unknown": "Prefer not to say",
      "comic.title": "Four-panel comic",
      "comic.generate": "Generate comic",
      "comic.generating": "Generating...",
      "comic.hint": "The comic button appears only when OpenAI image generation is configured.",
      "comic.empty": "No comic generated yet.",
      "review.back": "Back to console",
      "review.transcript": "Transcript",
      "review.notes": "Physician notes",
      "review.output": "Analysis result",
      "review.noOutput": "This visit has no generated output yet.",
      "portal.titleTail": "post-visit care",
      "portal.disclaimer": "This page supports post-visit care. Follow the clinician's instructions and medication labels. Seek care promptly if warning signs appear.",
      "portal.pdf": "Download post-visit PDF",
      "parent.title": "Your child's post-visit care",
      "parent.subtitle": "Review recent visit summaries, parent education, child-friendly guidance, and generated comics when available.",
      "parent.open": "Open",
      "parent.empty": "No visits are linked to this parent account yet.",
      "message.selectPatient": "Please enter or choose a patient first.",
      "message.stopFirst": "Please stop the current recording before switching patients.",
      "message.created": "Case created.",
      "message.browserUnsupported": "This browser does not support live speech recognition. Try Chrome or Edge.",
      "message.recognitionStarted": "Live transcription is already starting. Please wait.",
      "message.micFailed": "Unable to start the microphone. Check browser permissions.",
      "message.resumeFailed": "Live transcription has not resumed yet. Try Resume again.",
      "message.emptyTranscript": "The transcript is empty. Please record first.",
      "message.analysisWorking": "OpenPediCare is combining patient details, transcript, and notes...",
      "message.analysisDone": "Analysis complete.",
      "message.comicDone": "Comic generated.",
      "record.readyTitle": "Ready to record",
      "record.readyHelp": "Chrome and Edge can show a read-only live transcript. Each sentence is placed on a new line.",
      "record.liveTitle": "Recording and transcribing",
      "record.liveHelp": "Speak naturally. Sentences will be separated into new lines, then you can add physician notes.",
      "record.pausedTitle": "Recording paused",
      "record.pausedHelp": "Tap Resume to continue the same transcript without duplicating previous text.",
      "record.stoppedTitle": "Recording stopped",
      "record.stoppedHelp": "The read-only transcript is saved. Skip notes or add physician context before analysis.",
      "record.interim": "Live",
      "label.years": "years",
      "label.unspecified": "Unspecified",
    },
    "zh-Hant": {
      "nav.doctor": "醫師工作台",
      "nav.parent": "家長介面",
      "nav.logout": "登出",
      "nav.signIn": "登入",
      "home.kicker": "兒童科 AI 智慧診後照護工作台",
      "home.copy": "把兒科門診對話轉成清楚的看診摘要、家長衛教、兒童友善說明與可分享的診後文件。",
      "home.tryDemo": "試用 Demo",
      "home.note1": "OpenPediCare 是診後照護與溝通輔助工具，不取代醫師臨床判斷。",
      "home.note2": "參考 PostVisit 類型的擷取、脈絡整合、多受眾輸出流程。",
      "login.title": "登入工作台",
      "login.copy": "Demo 帳號可進入醫師與家長流程；正式上線前請更換密碼並填入 `.env` 金鑰。",
      "login.account": "帳號",
      "login.password": "密碼",
      "login.demoDoctor": "Demo 醫師",
      "login.demoParent": "Demo 家長",
      "doctor.title": "兒科即時語音看診",
      "doctor.subtitle": "輸入兒童基本資料，開始錄音後即時轉成唯讀逐字稿；停止後可補醫師備註，接著產生看診摘要與衛教內容。",
      "doctor.metricPatients": "患者",
      "doctor.metricAnalyses": "分析",
      "doctor.metricSpeech": "語音",
      "doctor.tabVisit": "即時看診",
      "doctor.tabHistory": "近期分析",
      "doctor.flowPatient": "患者資料",
      "doctor.flowPatientSmall": "姓名、年齡、性別",
      "doctor.flowRecord": "即時錄音",
      "doctor.flowRecordSmall": "語音轉逐字稿",
      "doctor.flowNote": "補充備註",
      "doctor.flowNoteSmall": "跳過或加入醫囑",
      "doctor.flowResult": "分析",
      "doctor.flowResultSmall": "摘要與衛教",
      "doctor.patientTitle": "兒童基本資料",
      "doctor.patientName": "姓名",
      "doctor.patientNamePlaceholder": "Demo Child",
      "doctor.patientAge": "年齡",
      "doctor.patientSex": "性別",
      "doctor.createAndRecord": "建立個案並開始錄音",
      "doctor.returningTitle": "回診患者",
      "doctor.returningCopy": "回診患者放在看診流程中選擇，讓歷史分頁專注保留已完成分析。",
      "doctor.returningPlaceholder": "選擇既有兒童",
      "doctor.startFollowUp": "開始回診看診",
      "doctor.currentPatient": "目前個案",
      "doctor.recordTitle": "即時錄音與轉寫",
      "doctor.recordReadyTitle": "準備開始錄音",
      "doctor.recordReadyHelp": "Chrome / Edge 可顯示唯讀即時逐字稿；每句話會自動換行。",
      "doctor.startRecording": "開始錄音",
      "doctor.pause": "暫停",
      "doctor.resume": "繼續",
      "doctor.stopRecording": "停止錄音",
      "doctor.transcript": "即時逐字稿",
      "doctor.transcriptPlaceholder": "錄音後逐句顯示。此區為唯讀，不需手動修改。",
      "doctor.noteTitle": "是否補充醫師備註？",
      "doctor.noteCopy": "停止錄音後，可補充重要醫囑、用藥原文、回診安排或家長疑問；也可以直接跳過。",
      "doctor.notesLabel": "醫師補充內容",
      "doctor.notesPlaceholder": "例如：若呼吸急促、嗜睡或尿量明顯減少需立即就醫。",
      "doctor.skipAnalyze": "跳過並分析",
      "doctor.addAnalyze": "加入備註並分析",
      "doctor.outputTitle": "分析結果",
      "doctor.summaryTab": "看診摘要",
      "doctor.parentTab": "家長衛教",
      "doctor.patientTab": "患者衛教",
      "doctor.outputEmpty": "停止錄音並完成備註選擇後，分析結果會顯示在這裡。",
      "doctor.parentLink": "家長查閱連結",
      "doctor.recentTitle": "近期分析",
      "doctor.notReady": "尚未產生",
      "doctor.noAnalyses": "尚未建立分析。",
      "doctor.viewResult": "查看",
      "status.idle": "待開始",
      "status.waiting": "等待中",
      "status.socketReady": "錄音通道準備完成",
      "status.recording": "錄音中",
      "status.paused": "暫停中",
      "status.notes": "等待備註",
      "status.processing": "分析中",
      "status.done": "完成",
      "status.failed": "失敗",
      "status.disconnected": "連線中斷",
      "gender.female": "女",
      "gender.male": "男",
      "gender.other": "其他",
      "gender.unknown": "未填",
      "comic.title": "四宮格漫畫",
      "comic.generate": "生成漫畫",
      "comic.generating": "生成中...",
      "comic.hint": "填入 OpenAI 圖像金鑰後才會顯示生成漫畫按鈕。",
      "comic.empty": "尚未生成漫畫。",
      "review.back": "返回工作台",
      "review.transcript": "門診轉寫",
      "review.notes": "醫師補充",
      "review.output": "分析結果",
      "review.noOutput": "此診次尚未產生輸出。",
      "portal.titleTail": "診後照護",
      "portal.disclaimer": "此頁面為診後照護輔助，請依醫師當次說明與藥袋標示執行。若出現警示徵兆，請立即就醫。",
      "portal.pdf": "下載診後 PDF",
      "parent.title": "孩子的診後照護",
      "parent.subtitle": "查看近期看診摘要、家長衛教、孩子友善說明與已生成的漫畫。",
      "parent.open": "開啟",
      "parent.empty": "目前沒有連到此家長帳號的診次。",
      "message.selectPatient": "請先輸入或選擇患者。",
      "message.stopFirst": "請先停止目前錄音，再切換患者。",
      "message.created": "個案已建立。",
      "message.browserUnsupported": "此瀏覽器不支援即時語音轉錄，請改用 Chrome / Edge。",
      "message.recognitionStarted": "即時轉錄已啟動過，請稍候。",
      "message.micFailed": "無法啟動麥克風，請確認瀏覽器權限。",
      "message.resumeFailed": "即時轉錄尚未恢復，請稍候再按一次繼續。",
      "message.emptyTranscript": "逐字稿是空的，請先錄音。",
      "message.analysisWorking": "OpenPediCare 正在整合患者資料、逐字稿與醫師補充內容...",
      "message.analysisDone": "分析完成。",
      "message.comicDone": "漫畫已生成。",
      "record.readyTitle": "準備開始看診錄音",
      "record.readyHelp": "Chrome / Edge 可顯示唯讀即時逐字稿；每句話會自動換行。",
      "record.liveTitle": "正在錄音與即時轉寫",
      "record.liveHelp": "請自然看診；逐字稿會逐句換行顯示，停止後可補充醫師備註。",
      "record.pausedTitle": "錄音已暫停",
      "record.pausedHelp": "按「繼續」即可接續同一份逐字稿，不會重複帶入上一段內容。",
      "record.stoppedTitle": "錄音已停止",
      "record.stoppedHelp": "逐字稿已保存為唯讀內容；可選擇跳過或補充醫師備註進行分析。",
      "record.interim": "即時",
      "label.years": "歲",
      "label.unspecified": "未填",
    },
  };

  function getLang() {
    try {
      return window.localStorage.getItem("openpedicare_lang") || "en";
    } catch (error) {
      return "en";
    }
  }

  function setLang(lang) {
    try {
      window.localStorage.setItem("openpedicare_lang", lang);
    } catch (error) {
      // localStorage may be disabled.
    }
    applyLanguage(lang);
  }

  function t(key) {
    const lang = getLang();
    return I18N[lang]?.[key] || I18N.en[key] || key;
  }

  function applyLanguage(lang = getLang()) {
    document.documentElement.lang = lang === "zh-Hant" ? "zh-Hant" : "en";
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      node.textContent = I18N[lang]?.[node.dataset.i18n] || I18N.en[node.dataset.i18n] || node.textContent;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
      node.placeholder = I18N[lang]?.[node.dataset.i18nPlaceholder] || I18N.en[node.dataset.i18nPlaceholder] || node.placeholder;
    });
    const toggle = document.querySelector("#language-toggle");
    if (toggle) {
      toggle.textContent = lang === "zh-Hant" ? "English" : "中文";
    }
  }

  function initLanguageToggle() {
    applyLanguage(getLang());
    document.querySelector("#language-toggle")?.addEventListener("click", () => {
      setLang(getLang() === "zh-Hant" ? "en" : "zh-Hant");
    });
  }

  function jsonFetch(url, options = {}) {
    return fetch(url, {
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
        ...(options.headers || {}),
      },
      ...options,
    }).then(async (response) => {
      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.ok === false) {
        throw new Error(data.error?.message || "Request failed");
      }
      return data;
    });
  }

  function toast(message, type = "info") {
    const stack = document.querySelector(".flash-stack") || document.body.appendChild(Object.assign(document.createElement("div"), { className: "flash-stack" }));
    const node = document.createElement("div");
    node.className = `flash ${type}`;
    node.textContent = message;
    stack.appendChild(node);
    setTimeout(() => node.remove(), 3600);
  }

  function escapeHtml(value) {
    return String(value || "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
  }

  function activeTab(buttons, activeButton) {
    buttons.forEach((button) => button.classList.toggle("active", button === activeButton));
  }

  function initPortalTabs() {
    const buttons = Array.from(document.querySelectorAll("[data-portal-tab]"));
    if (!buttons.length) return;
    const panels = Array.from(document.querySelectorAll("[data-portal-panel]"));
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const name = button.dataset.portalTab;
        activeTab(buttons, button);
        panels.forEach((panel) => panel.classList.toggle("hidden", panel.dataset.portalPanel !== name));
      });
    });
  }

  async function generateComicForVisit(visitId) {
    return jsonFetch(`/api/output/${visitId}/comic`, { method: "POST", body: JSON.stringify({}) });
  }

  function initStandaloneComicButtons() {
    document.querySelectorAll("[data-generate-comic]").forEach((button) => {
      button.addEventListener("click", async () => {
        const box = button.closest(".comic-box");
        const visitId = box?.dataset.visitId;
        if (!visitId) return;
        button.disabled = true;
        button.textContent = t("comic.generating");
        try {
          const data = await generateComicForVisit(visitId);
          const src = data.output?.comic_image_url;
          if (src) {
            let image = box.querySelector(".comic-image");
            box.querySelector(".muted")?.remove();
            if (!image) {
              image = document.createElement("img");
              image.className = "comic-image";
              image.alt = "Generated four-panel education comic";
              box.appendChild(image);
            }
            image.src = src;
            image.hidden = false;
          }
          toast(t("message.comicDone"), "success");
        } catch (error) {
          toast(error.message, "error");
        } finally {
          button.disabled = false;
          button.textContent = t("comic.generate");
        }
      });
    });
  }

  function initDashboard() {
    const shell = document.querySelector('[data-page="doctor-dashboard"]');
    if (!shell) return;

    const patientForm = document.querySelector("#patient-form");
    const returningSelect = document.querySelector("#returning-patient-select");
    const useReturningButton = document.querySelector("#use-returning-patient");
    const currentPatientBox = document.querySelector("#current-patient");
    const currentPatientText = currentPatientBox?.querySelector("strong");
    const startButton = document.querySelector("#start-recording");
    const pauseButton = document.querySelector("#pause-recording");
    const stopButton = document.querySelector("#stop-recording");
    const transcript = document.querySelector("#transcript");
    const doctorNotes = document.querySelector("#doctor-notes");
    const skipNoteButton = document.querySelector("#skip-note");
    const analyzeButton = document.querySelector("#analyze-with-note");
    const outputContent = document.querySelector("#output-content");
    const tabButtons = Array.from(document.querySelectorAll("[data-tab]"));
    const dashboardTabs = Array.from(document.querySelectorAll("[data-dashboard-tab]"));
    const dashboardPanels = Array.from(document.querySelectorAll("[data-dashboard-panel]"));
    const sessionStatus = document.querySelector("#session-status");
    const analysisState = document.querySelector("#analysis-state");
    const recordOrb = document.querySelector("#record-orb");
    const recordTitle = document.querySelector("#record-title-dynamic");
    const recordHelper = document.querySelector("#record-helper");
    const noteCard = document.querySelector("#note-card");
    const shareBox = document.querySelector("#share-box");
    const shareAnchor = shareBox?.querySelector("a");
    const comicBox = document.querySelector("#comic-box");
    const generateComicButton = document.querySelector("#generate-comic");
    const comicImage = document.querySelector("#comic-image");
    const comicHint = document.querySelector("#comic-hint");
    const flowItems = Array.from(document.querySelectorAll("[data-flow]"));

    let currentPatient = null;
    let visitId = null;
    let socket = null;
    let recordStream = null;
    let mediaRecorder = null;
    let recognition = null;
    let isRecording = false;
    let isPaused = false;
    let transcriptLines = [];
    let activeInterim = "";
    let currentOutput = null;
    let currentTab = "summary";

    function setStatus(label, mode = "idle") {
      sessionStatus.textContent = label;
      sessionStatus.className = `status-pill ${mode}`;
    }

    function setAnalysisState(label, mode = "idle") {
      if (!analysisState) return;
      analysisState.textContent = label;
      analysisState.className = `status-pill ${mode}`;
    }

    function setFlow(activeName) {
      let seenActive = false;
      flowItems.forEach((item) => {
        const isActive = item.dataset.flow === activeName;
        item.classList.toggle("active", isActive);
        item.classList.toggle("done", !isActive && !seenActive);
        if (isActive) seenActive = true;
      });
    }

    function showDashboardPanel(name) {
      const activeButton = dashboardTabs.find((button) => button.dataset.dashboardTab === name);
      if (activeButton) activeTab(dashboardTabs, activeButton);
      dashboardPanels.forEach((panel) => {
        panel.hidden = panel.dataset.dashboardPanel !== name;
      });
    }

    function normalizeLine(value) {
      return String(value || "").replace(/\s+/g, " ").trim();
    }

    function splitSentences(value) {
      const normalized = normalizeLine(value);
      if (!normalized) return [];
      const parts = normalized.match(/[^。！？!?；;.\n]+[。！？!?；;.]?/g) || [normalized];
      return parts.map((part) => normalizeLine(part)).filter(Boolean);
    }

    function renderTranscript() {
      const lines = transcriptLines.slice();
      if (activeInterim) lines.push(`(${t("record.interim")}) ${activeInterim}`);
      transcript.value = lines.join("\n");
      transcript.scrollTop = transcript.scrollHeight;
    }

    function setTranscriptText(value) {
      transcriptLines = String(value || "")
        .split(/\n+/)
        .map((line) => normalizeLine(line.replace(/^\(.*?\)\s*/, "").replace(/^（即時）/, "")))
        .filter(Boolean);
      activeInterim = "";
      renderTranscript();
    }

    function appendTranscriptText(value, shouldRender = true) {
      splitSentences(value).forEach((sentence) => {
        const previous = transcriptLines[transcriptLines.length - 1] || "";
        if (normalizeLine(previous) === sentence) return;
        transcriptLines.push(sentence);
      });
      if (shouldRender) renderTranscript();
    }

    function transcriptText() {
      return transcriptLines.join("\n").trim();
    }

    function renderComic() {
      if (!comicBox || !currentOutput) return;
      const hasImage = Boolean(currentOutput.comic_image_url);
      const canGenerate = Boolean(currentOutput.comic_generation_enabled && generateComicButton);
      comicBox.hidden = !(hasImage || canGenerate);
      if (comicHint) comicHint.hidden = hasImage || canGenerate;
      if (comicImage) {
        comicImage.hidden = !hasImage;
        if (hasImage) comicImage.src = currentOutput.comic_image_url;
      }
    }

    function resetOutput() {
      currentOutput = null;
      currentTab = "summary";
      activeTab(tabButtons, tabButtons[0]);
      outputContent.classList.add("empty-state");
      outputContent.innerHTML = `<p>${escapeHtml(t("doctor.outputEmpty"))}</p>`;
      shareBox.hidden = true;
      if (comicBox) comicBox.hidden = true;
      if (comicImage) {
        comicImage.hidden = true;
        comicImage.removeAttribute("src");
      }
      setAnalysisState(t("status.waiting"), "idle");
    }

    function resetVisitState() {
      if (socket) socket.close();
      socket = null;
      visitId = null;
      isRecording = false;
      isPaused = false;
      recognition = null;
      mediaRecorder = null;
      recordStream = null;
      transcriptLines = [];
      activeInterim = "";
      renderTranscript();
      doctorNotes.value = "";
      startButton.disabled = !currentPatient;
      pauseButton.disabled = true;
      pauseButton.textContent = t("doctor.pause");
      stopButton.disabled = true;
      skipNoteButton.disabled = true;
      analyzeButton.disabled = true;
      noteCard.classList.add("locked");
      noteCard.classList.remove("ready");
      recordOrb.classList.remove("recording");
      recordTitle.textContent = t("record.readyTitle");
      recordHelper.textContent = t("record.readyHelp");
      setStatus(t("status.idle"), "idle");
      resetOutput();
    }

    function patientLabel(patient) {
      const gender = patient.gender_label || patient.gender || t("label.unspecified");
      return `${patient.name} · ${patient.age_years} ${t("label.years")} · ${gender}`;
    }

    function setCurrentPatient(patient) {
      currentPatient = patient;
      currentPatientBox.hidden = false;
      currentPatientText.textContent = patientLabel(patient);
      if (returningSelect) returningSelect.value = String(patient.id);
      resetVisitState();
      setFlow("record");
      showDashboardPanel("visit");
    }

    function appendReturningOption(patient) {
      if (!returningSelect) return;
      const option = document.createElement("option");
      option.value = patient.id;
      option.dataset.patientName = patient.name;
      option.dataset.patientAge = patient.age_years;
      option.dataset.patientGender = patient.gender_label || patient.gender || t("label.unspecified");
      option.textContent = patientLabel(patient);
      returningSelect.appendChild(option);
      useReturningButton.disabled = false;
      setCurrentPatient(patient);
    }

    function connectSocket() {
      if (!visitId) return;
      if (socket) socket.close();
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      socket = new WebSocket(`${protocol}://${window.location.host}/api/visit/transcribe/?visit_id=${visitId}`);
      socket.addEventListener("open", () => setStatus(t("status.socketReady"), "live"));
      socket.addEventListener("message", (event) => {
        const payload = JSON.parse(event.data);
        if (payload.transcript && !isRecording) {
          setTranscriptText(payload.transcript);
        }
      });
      socket.addEventListener("close", () => {
        if (isRecording) setStatus(t("status.disconnected"), "idle");
      });
    }

    async function beginVisit(patient) {
      const data = await jsonFetch("/api/visit/start", {
        method: "POST",
        body: JSON.stringify({ patient_id: patient.id }),
      });
      visitId = data.session_id;
      connectSocket();
      return data.visit;
    }

    function sendTranscriptSnapshot() {
      const text = transcriptText();
      if (socket && socket.readyState === WebSocket.OPEN && text) {
        socket.send(JSON.stringify({ type: "transcript_replace", text }));
      }
    }

    function createSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return null;
      const instance = new SpeechRecognition();
      instance.lang = "zh-TW";
      instance.continuous = true;
      instance.interimResults = true;
      instance.maxAlternatives = 1;
      instance.onresult = (event) => {
        if (isPaused) return;
        const interimParts = [];
        for (let index = event.resultIndex; index < event.results.length; index += 1) {
          const phrase = event.results[index][0].transcript;
          if (event.results[index].isFinal) {
            appendTranscriptText(phrase, false);
          } else {
            interimParts.push(phrase);
          }
        }
        activeInterim = normalizeLine(interimParts.join(" "));
        renderTranscript();
      };
      instance.onerror = (event) => {
        if (["aborted", "no-speech"].includes(event.error)) return;
        toast(`Live transcription paused: ${event.error}`, "error");
      };
      instance.onend = () => {
        if (!isRecording || isPaused) return;
        window.setTimeout(() => {
          if (!isRecording || isPaused) return;
          try {
            instance.start();
          } catch (error) {
            setStatus(t("status.paused"), "idle");
          }
        }, 250);
      };
      return instance;
    }

    async function startRecording() {
      if (isRecording && isPaused) {
        resumeRecording();
        return;
      }
      if (!currentPatient) {
        toast(t("message.selectPatient"), "error");
        return;
      }
      if (!visitId) {
        await beginVisit(currentPatient);
      }

      isRecording = true;
      isPaused = false;
      activeInterim = "";
      setFlow("record");
      setStatus(t("status.recording"), "live");
      recordOrb.classList.add("recording");
      recordTitle.textContent = t("record.liveTitle");
      recordHelper.textContent = t("record.liveHelp");
      startButton.disabled = true;
      pauseButton.disabled = false;
      pauseButton.textContent = t("doctor.pause");
      stopButton.disabled = false;
      skipNoteButton.disabled = true;
      analyzeButton.disabled = true;
      noteCard.classList.add("locked");
      noteCard.classList.remove("ready");

      recognition = createSpeechRecognition();
      if (recognition) {
        try {
          recognition.start();
        } catch (error) {
          toast(t("message.recognitionStarted"), "error");
        }
      } else {
        toast(t("message.browserUnsupported"), "error");
      }

      if (navigator.mediaDevices?.getUserMedia) {
        try {
          recordStream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaRecorder = new MediaRecorder(recordStream);
          mediaRecorder.addEventListener("dataavailable", (event) => {
            if (!event.data.size || !socket || socket.readyState !== WebSocket.OPEN) return;
            const reader = new FileReader();
            reader.onloadend = () => socket.send(JSON.stringify({ type: "audio", mime_type: event.data.type, data: reader.result }));
            reader.readAsDataURL(event.data);
          });
          mediaRecorder.start(5000);
        } catch (error) {
          toast(t("message.micFailed"), "error");
        }
      }
    }

    function pauseRecording() {
      if (!isRecording || isPaused) return;
      isPaused = true;
      activeInterim = "";
      renderTranscript();
      try {
        recognition?.stop();
      } catch (error) {
        // SpeechRecognition may already be stopped.
      }
      if (mediaRecorder?.state === "recording") {
        mediaRecorder.pause();
      }
      recordOrb.classList.remove("recording");
      pauseButton.textContent = t("doctor.resume");
      setStatus(t("status.paused"), "processing");
      recordTitle.textContent = t("record.pausedTitle");
      recordHelper.textContent = t("record.pausedHelp");
      sendTranscriptSnapshot();
    }

    function resumeRecording() {
      if (!isRecording || !isPaused) return;
      isPaused = false;
      recordOrb.classList.add("recording");
      pauseButton.textContent = t("doctor.pause");
      setStatus(t("status.recording"), "live");
      recordTitle.textContent = t("record.liveTitle");
      recordHelper.textContent = t("record.liveHelp");
      try {
        recognition?.start();
      } catch (error) {
        recognition = createSpeechRecognition();
        try {
          recognition?.start();
        } catch (innerError) {
          toast(t("message.resumeFailed"), "error");
        }
      }
      if (mediaRecorder?.state === "paused") {
        mediaRecorder.resume();
      }
    }

    function togglePause() {
      if (isPaused) {
        resumeRecording();
      } else {
        pauseRecording();
      }
    }

    function stopRecording() {
      if (!isRecording && !visitId) return;
      isRecording = false;
      isPaused = false;
      activeInterim = "";
      renderTranscript();
      try {
        recognition?.stop();
      } catch (error) {
        // SpeechRecognition may already be stopped.
      }
      recognition = null;
      if (mediaRecorder && ["recording", "paused"].includes(mediaRecorder.state)) {
        mediaRecorder.stop();
      }
      mediaRecorder = null;
      recordStream?.getTracks().forEach((track) => track.stop());
      recordStream = null;
      recordOrb.classList.remove("recording");
      startButton.disabled = false;
      pauseButton.disabled = true;
      pauseButton.textContent = t("doctor.pause");
      stopButton.disabled = true;
      skipNoteButton.disabled = false;
      analyzeButton.disabled = false;
      noteCard.classList.remove("locked");
      noteCard.classList.add("ready");
      setFlow("note");
      setStatus(t("status.notes"), "processing");
      recordTitle.textContent = t("record.stoppedTitle");
      recordHelper.textContent = t("record.stoppedHelp");
      sendTranscriptSnapshot();
    }

    async function analyze(doctorNoteValue) {
      if (!visitId) return;
      const text = transcriptText();
      if (!text) {
        toast(t("message.emptyTranscript"), "error");
        return;
      }

      try {
        setFlow("result");
        setStatus(t("status.processing"), "processing");
        setAnalysisState(t("status.processing"), "processing");
        outputContent.classList.add("empty-state");
        outputContent.innerHTML = `<p>${escapeHtml(t("message.analysisWorking"))}</p>`;
        skipNoteButton.disabled = true;
        analyzeButton.disabled = true;
        const data = await jsonFetch("/api/visit/complete", {
          method: "POST",
          body: JSON.stringify({
            visit_id: visitId,
            transcript: text,
            doctor_notes: doctorNoteValue || "",
          }),
        });
        currentOutput = data.output;
        renderOutput();
        setStatus(t("status.done"), "live");
        setAnalysisState(t("status.done"), "live");
        toast(t("message.analysisDone"), "success");
      } catch (error) {
        setStatus(t("status.failed"), "idle");
        setAnalysisState(t("status.failed"), "idle");
        skipNoteButton.disabled = false;
        analyzeButton.disabled = false;
        toast(error.message, "error");
      }
    }

    function renderOutput() {
      if (!currentOutput) return;
      const map = {
        summary: currentOutput.visit_summary || currentOutput.parent_summary,
        parent: currentOutput.parent_education || currentOutput.school_note,
        patient: currentOutput.patient_education || currentOutput.child_explanation,
      };
      outputContent.classList.remove("empty-state");
      outputContent.innerHTML = `<p>${escapeHtml(map[currentTab] || "")}</p>`;
      if (currentOutput.share_url) {
        shareAnchor.href = currentOutput.share_url;
        shareAnchor.textContent = `${window.location.origin}${currentOutput.share_url}`;
        shareBox.hidden = false;
      }
      renderComic();
    }

    dashboardTabs.forEach((button) => {
      button.addEventListener("click", () => showDashboardPanel(button.dataset.dashboardTab));
    });

    patientForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (isRecording) {
        toast(t("message.stopFirst"), "error");
        return;
      }
      const payload = Object.fromEntries(new FormData(patientForm).entries());
      try {
        setStatus(t("message.created"), "processing");
        const patientData = await jsonFetch("/api/patient", { method: "POST", body: JSON.stringify(payload) });
        appendReturningOption(patientData.patient);
        patientForm.reset();
        patientForm.querySelector('[name="age_years"]').value = "7";
        await beginVisit(patientData.patient);
        await startRecording();
      } catch (error) {
        setStatus(t("status.idle"), "idle");
        toast(error.message, "error");
      }
    });

    useReturningButton?.addEventListener("click", async () => {
      if (isRecording) {
        toast(t("message.stopFirst"), "error");
        return;
      }
      const option = returningSelect?.selectedOptions?.[0];
      if (!option || !option.value) {
        toast(t("message.selectPatient"), "error");
        return;
      }
      const patient = {
        id: option.value,
        name: option.dataset.patientName,
        age_years: option.dataset.patientAge,
        gender_label: option.dataset.patientGender,
      };
      try {
        setCurrentPatient(patient);
        await beginVisit(patient);
        await startRecording();
      } catch (error) {
        setStatus(t("status.idle"), "idle");
        toast(error.message, "error");
      }
    });

    startButton?.addEventListener("click", () => {
      startRecording().catch((error) => toast(error.message, "error"));
    });
    pauseButton?.addEventListener("click", togglePause);
    stopButton?.addEventListener("click", stopRecording);
    skipNoteButton?.addEventListener("click", () => analyze(""));
    analyzeButton?.addEventListener("click", () => analyze(doctorNotes.value.trim()));

    tabButtons.forEach((button) => {
      button.addEventListener("click", () => {
        currentTab = button.dataset.tab;
        activeTab(tabButtons, button);
        renderOutput();
      });
    });

    generateComicButton?.addEventListener("click", async () => {
      if (!currentOutput?.visit_id) return;
      generateComicButton.disabled = true;
      generateComicButton.textContent = t("comic.generating");
      try {
        const data = await generateComicForVisit(currentOutput.visit_id);
        currentOutput = data.output;
        renderComic();
        toast(t("message.comicDone"), "success");
      } catch (error) {
        toast(error.message, "error");
      } finally {
        generateComicButton.disabled = false;
        generateComicButton.textContent = t("comic.generate");
      }
    });
  }

  initLanguageToggle();
  initPortalTabs();
  initStandaloneComicButtons();
  initDashboard();
})();
