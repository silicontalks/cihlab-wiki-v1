const workspacePath = window.CIHLAB_WORKSPACE_PATH || "";
const state = {
  currentUser: null,
  projects: [],
  selectedProject: null,
  activeTab: "tasks",
  projectDialogMode: "create",
  projectPendingDeletion: null,
  knowledgeContent: "",
  knowledgeFilePath: "",
  knowledgeLoadedProjectId: null,
  knowledgeSaving: false,
  milestones: [],
  milestonesLoadedProjectId: null,
  selectedMilestoneId: null,
  milestoneDialogMode: "create",
  progressTasks: [],
  progressTasksLoadedProjectId: null,
  selectedProgressTaskId: null,
  progressTaskDialogMode: "create",
  progressScale: "quarter",
  rawFiles: [],
  rawFilesLoadedProjectId: null,
  rawFileUploading: false,
  equipmentFiles: [],
  equipmentFilesLoadedProjectId: null,
  equipmentFileUploading: false,
  equipmentPlans: [],
  equipmentPlansLoadedProjectId: null,
  selectedEquipmentPlanId: null,
  equipmentPlanDialogMode: "create",
  financeFiles: [],
  financeFilesLoadedProjectId: null,
  financeFileUploading: false,
  papers: [],
  patents: [],
  publicationsLoadedProjectId: null,
  publicationDialogType: "paper",
  publicationUploading: false,
  publicationTargetSaving: false,
  meetings: [],
  meetingsLoadedProjectId: null,
  lastMeetingDate: "",
  lastActionItems: "",
  meetingProgress: "",
  meetingActionItems: "",
  meetingSaving: false,
  tests: [],
  testsLoadedProjectId: null,
  selectedTestId: null,
  testDialogMode: "create",
  people: [],
  peopleLoadedProjectId: null,
};

const tabConfig = {
  tasks: {
    label: "项目总体进展",
    title: "项目总体进展",
    headers: ["课题名称", "任务名称", "负责人", "完成进度", "当前进展描述"],
  },
  nodeAlerts: {
    label: "节点提醒",
    title: "节点提醒列表",
    headers: ["提醒日期", "负责人", "节点目标", "考核方式", "状态"],
  },
  publications: {
    label: "论文/专利",
    title: "论文/专利列表",
    headers: ["序号", "名称", "作者/发明人", "状态", "下载", "备注"],
  },
  meetings: {
    label: "项目例会",
    title: "例会记录",
    headers: ["日期", "Progress", "Action Item"],
  },
  tests: {
    label: "项目测试",
    title: "测试指标表",
    headers: ["课题/待测物名称", "指标名称", "预期中期指标", "预期完成指标", "是否第三方测试", "测试大纲缩略版"],
  },
  equipment: {
    label: "设备/IP/流片",
    title: "设备/IP/流片记录",
    headers: ["类型", "名称", "负责人", "当前状态", "备注"],
  },
  finance: {
    label: "财务情况更新",
    title: "财务记录",
    headers: ["日期", "类别", "金额", "经办人", "说明"],
  },
  people: {
    label: "人员信息",
    title: "人员信息表",
    headers: ["姓名", "角色", "单位", "联系方式", "备注"],
  },
  raw: {
    label: "项目文档",
    title: "项目文档列表",
    headers: ["文件名称", "文件类型", "文件路径", "备注"],
  },
  knowledge: {
    label: "知识库",
    title: "知识库条目",
    headers: ["标题", "分类", "关键词", "来源/链接", "备注"],
  },
};

const elements = {
  loginView: document.querySelector("#loginView"),
  loginForm: document.querySelector("#loginForm"),
  loginUsername: document.querySelector("#loginUsername"),
  loginPassword: document.querySelector("#loginPassword"),
  loginError: document.querySelector("#loginError"),
  logoutButton: document.querySelector("#logoutButton"),
  currentUserLabel: document.querySelector("#currentUserLabel"),
  projectList: document.querySelector("#projectList"),
  searchInput: document.querySelector("#searchInput"),
  createProjectButton: document.querySelector("#createProjectButton"),
  editProjectButton: document.querySelector("#editProjectButton"),
  projectStatus: document.querySelector("#projectStatus"),
  projectTitle: document.querySelector("#projectTitle"),
  sourceValue: document.querySelector("#sourceValue"),
  startDateValue: document.querySelector("#startDateValue"),
  endDateValue: document.querySelector("#endDateValue"),
  budgetValue: document.querySelector("#budgetValue"),
  partnersValue: document.querySelector("#partnersValue"),
  ownerValue: document.querySelector("#ownerValue"),
  financeOwnerValue: document.querySelector("#financeOwnerValue"),
  technicalContactValue: document.querySelector("#technicalContactValue"),
  activeTabLabel: document.querySelector("#activeTabLabel"),
  panelTitle: document.querySelector("#panelTitle"),
  panelAddButton: document.querySelector("#panelAddButton"),
  panelContent: document.querySelector("#panelContent"),
  tabs: document.querySelectorAll(".tab"),
  projectDialog: document.querySelector("#projectDialog"),
  projectForm: document.querySelector("#projectForm"),
  projectDialogTitle: document.querySelector("#projectDialogTitle"),
  closeProjectDialogButton: document.querySelector("#closeProjectDialogButton"),
  cancelProjectFormButton: document.querySelector("#cancelProjectFormButton"),
  projectFormError: document.querySelector("#projectFormError"),
  deleteProjectDialog: document.querySelector("#deleteProjectDialog"),
  deleteProjectForm: document.querySelector("#deleteProjectForm"),
  closeDeleteProjectDialogButton: document.querySelector("#closeDeleteProjectDialogButton"),
  cancelDeleteProjectButton: document.querySelector("#cancelDeleteProjectButton"),
  deleteProjectMessage: document.querySelector("#deleteProjectMessage"),
  deleteProjectFolderCheckbox: document.querySelector("#deleteProjectFolderCheckbox"),
  deleteProjectError: document.querySelector("#deleteProjectError"),
  milestoneDialog: document.querySelector("#milestoneDialog"),
  milestoneForm: document.querySelector("#milestoneForm"),
  milestoneDialogTitle: document.querySelector("#milestoneDialogTitle"),
  closeMilestoneDialogButton: document.querySelector("#closeMilestoneDialogButton"),
  cancelMilestoneFormButton: document.querySelector("#cancelMilestoneFormButton"),
  milestoneFormError: document.querySelector("#milestoneFormError"),
  milestoneFormFields: {
    due_date: document.querySelector("#milestoneDueDate"),
    owner: document.querySelector("#milestoneOwner"),
    target: document.querySelector("#milestoneTarget"),
    assessment: document.querySelector("#milestoneAssessment"),
    status: document.querySelector("#milestoneStatus"),
    note: document.querySelector("#milestoneNote"),
  },
  progressTaskDialog: document.querySelector("#progressTaskDialog"),
  progressTaskForm: document.querySelector("#progressTaskForm"),
  progressTaskDialogTitle: document.querySelector("#progressTaskDialogTitle"),
  closeProgressTaskDialogButton: document.querySelector("#closeProgressTaskDialogButton"),
  cancelProgressTaskFormButton: document.querySelector("#cancelProgressTaskFormButton"),
  progressTaskFormError: document.querySelector("#progressTaskFormError"),
  progressTaskFormFields: {
    subject_name: document.querySelector("#progressSubjectName"),
    task_name: document.querySelector("#progressTaskName"),
    owner: document.querySelector("#progressOwner"),
    progress_percent: document.querySelector("#progressPercent"),
    start_date: document.querySelector("#progressStartDate"),
    end_date: document.querySelector("#progressEndDate"),
    status: document.querySelector("#progressStatus"),
    progress_note: document.querySelector("#progressNote"),
  },
  equipmentPlanDialog: document.querySelector("#equipmentPlanDialog"),
  equipmentPlanForm: document.querySelector("#equipmentPlanForm"),
  equipmentPlanDialogTitle: document.querySelector("#equipmentPlanDialogTitle"),
  closeEquipmentPlanDialogButton: document.querySelector("#closeEquipmentPlanDialogButton"),
  cancelEquipmentPlanFormButton: document.querySelector("#cancelEquipmentPlanFormButton"),
  equipmentPlanFormError: document.querySelector("#equipmentPlanFormError"),
  equipmentPlanFormFields: {
    plan_time: document.querySelector("#equipmentPlanTime"),
    budget: document.querySelector("#equipmentPlanBudget"),
    supplier: document.querySelector("#equipmentPlanSupplier"),
    closure_material_requirements: document.querySelector("#equipmentPlanClosureMaterials"),
  },
  personDialog: document.querySelector("#personDialog"),
  personForm: document.querySelector("#personForm"),
  closePersonDialogButton: document.querySelector("#closePersonDialogButton"),
  cancelPersonFormButton: document.querySelector("#cancelPersonFormButton"),
  personFormError: document.querySelector("#personFormError"),
  personFormFields: {
    sequence_no: document.querySelector("#personSequenceNo"),
    name: document.querySelector("#personName"),
    organization: document.querySelector("#personOrganization"),
    responsibility: document.querySelector("#personResponsibility"),
    id_number: document.querySelector("#personIdNumber"),
    email: document.querySelector("#personEmail"),
  },
  testDialog: document.querySelector("#testDialog"),
  testForm: document.querySelector("#testForm"),
  testDialogTitle: document.querySelector("#testDialogTitle"),
  closeTestDialogButton: document.querySelector("#closeTestDialogButton"),
  cancelTestFormButton: document.querySelector("#cancelTestFormButton"),
  testFormError: document.querySelector("#testFormError"),
  testFormFields: {
    subject_name: document.querySelector("#testSubjectName"),
    metric_name: document.querySelector("#testMetricName"),
    expected_midterm_metric: document.querySelector("#testMidtermMetric"),
    expected_final_metric: document.querySelector("#testFinalMetric"),
    third_party_test: document.querySelector("#testThirdParty"),
    test_outline_summary: document.querySelector("#testOutlineSummary"),
  },
  publicationDialog: document.querySelector("#publicationDialog"),
  publicationForm: document.querySelector("#publicationForm"),
  publicationDialogTitle: document.querySelector("#publicationDialogTitle"),
  closePublicationDialogButton: document.querySelector("#closePublicationDialogButton"),
  cancelPublicationFormButton: document.querySelector("#cancelPublicationFormButton"),
  publicationFormError: document.querySelector("#publicationFormError"),
  publicationFormFields: {
    sequence_no: document.querySelector("#publicationSequenceNo"),
    title: document.querySelector("#publicationTitle"),
    titleLabel: document.querySelector("#publicationTitleLabel"),
    paperAuthorsField: document.querySelector("#paperAuthorsField"),
    paperAuthors: document.querySelector("#paperAuthors"),
    patentApplicationNoField: document.querySelector("#patentApplicationNoField"),
    patentApplicationNo: document.querySelector("#patentApplicationNo"),
    patentStatusField: document.querySelector("#patentStatusField"),
    patentStatus: document.querySelector("#patentStatus"),
    patentInventorsField: document.querySelector("#patentInventorsField"),
    patentInventors: document.querySelector("#patentInventors"),
    labelType: document.querySelector("#publicationLabelType"),
    labelTypeLabel: document.querySelector("#publicationLabelTypeLabel"),
    file: document.querySelector("#publicationFile"),
    fileLabel: document.querySelector("#publicationFileLabel"),
    note: document.querySelector("#publicationNote"),
  },
  publicationTargetDialog: document.querySelector("#publicationTargetDialog"),
  publicationTargetForm: document.querySelector("#publicationTargetForm"),
  closePublicationTargetDialogButton: document.querySelector("#closePublicationTargetDialogButton"),
  cancelPublicationTargetFormButton: document.querySelector("#cancelPublicationTargetFormButton"),
  publicationTargetFormError: document.querySelector("#publicationTargetFormError"),
  publicationTargetFields: {
    paper_target_count: document.querySelector("#publicationPaperTargetCount"),
    patent_target_count: document.querySelector("#publicationPatentTargetCount"),
  },
  form: {
    name: document.querySelector("#formName"),
    source: document.querySelector("#formSource"),
    status: document.querySelector("#formStatus"),
    start_date: document.querySelector("#formStartDate"),
    end_date: document.querySelector("#formEndDate"),
    budget: document.querySelector("#formBudget"),
    owner: document.querySelector("#formOwner"),
    finance_owner: document.querySelector("#formFinanceOwner"),
    technical_contact: document.querySelector("#formTechnicalContact"),
    paper_target_count: document.querySelector("#formPaperTargetCount"),
    patent_target_count: document.querySelector("#formPatentTargetCount"),
    partners: document.querySelector("#formPartners"),
    description: document.querySelector("#formDescription"),
  },
};

async function api(path, options = {}) {
  const response = await fetch(withWorkspace(path), {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    credentials: "same-origin",
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "请求失败" }));
    throw new Error(error.detail || "请求失败");
  }
  return response.json();
}

async function initialize() {
  await fetch("/api/workspace/init", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify(workspacePath ? { workspace_path: workspacePath } : {}),
  });
  bindEvents();
  await checkLogin();
}

function withWorkspace(path) {
  if (!workspacePath) return path;
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}workspace_path=${encodeURIComponent(workspacePath)}`;
}

async function loadProjects() {
  const q = elements.searchInput.value.trim();
  const data = await api(`/api/projects${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  state.projects = data.items;
  if (!state.selectedProject && state.projects.length > 0) {
    state.selectedProject = state.projects[0];
  }
  if (state.selectedProject) {
    const latest = state.projects.find((project) => project.id === state.selectedProject.id);
    state.selectedProject = latest || state.projects[0] || null;
  }
  render();
}

function bindEvents() {
  elements.loginForm.addEventListener("submit", login);
  elements.logoutButton.addEventListener("click", logout);
  elements.createProjectButton.addEventListener("click", openCreateProjectDialog);
  elements.editProjectButton.addEventListener("click", openEditProjectDialog);
  elements.projectForm.addEventListener("submit", saveProjectForm);
  elements.closeProjectDialogButton.addEventListener("click", closeProjectDialog);
  elements.cancelProjectFormButton.addEventListener("click", closeProjectDialog);
  elements.deleteProjectForm.addEventListener("submit", confirmDeleteProject);
  elements.closeDeleteProjectDialogButton.addEventListener("click", closeDeleteProjectDialog);
  elements.cancelDeleteProjectButton.addEventListener("click", closeDeleteProjectDialog);
  elements.milestoneForm.addEventListener("submit", saveMilestoneForm);
  elements.closeMilestoneDialogButton.addEventListener("click", closeMilestoneDialog);
  elements.cancelMilestoneFormButton.addEventListener("click", closeMilestoneDialog);
  elements.progressTaskForm.addEventListener("submit", saveProgressTaskForm);
  elements.closeProgressTaskDialogButton.addEventListener("click", closeProgressTaskDialog);
  elements.cancelProgressTaskFormButton.addEventListener("click", closeProgressTaskDialog);
  elements.equipmentPlanForm.addEventListener("submit", saveEquipmentPlanForm);
  elements.closeEquipmentPlanDialogButton.addEventListener("click", closeEquipmentPlanDialog);
  elements.cancelEquipmentPlanFormButton.addEventListener("click", closeEquipmentPlanDialog);
  elements.personForm.addEventListener("submit", savePersonForm);
  elements.closePersonDialogButton.addEventListener("click", closePersonDialog);
  elements.cancelPersonFormButton.addEventListener("click", closePersonDialog);
  elements.testForm.addEventListener("submit", saveTestForm);
  elements.closeTestDialogButton.addEventListener("click", closeTestDialog);
  elements.cancelTestFormButton.addEventListener("click", closeTestDialog);
  elements.publicationForm.addEventListener("submit", savePublicationForm);
  elements.closePublicationDialogButton.addEventListener("click", closePublicationDialog);
  elements.cancelPublicationFormButton.addEventListener("click", closePublicationDialog);
  elements.publicationTargetForm.addEventListener("submit", savePublicationTargets);
  elements.closePublicationTargetDialogButton.addEventListener("click", closePublicationTargetDialog);
  elements.cancelPublicationTargetFormButton.addEventListener("click", closePublicationTargetDialog);
  elements.panelAddButton.addEventListener("click", () => {
    if (state.activeTab === "nodeAlerts") openCreateMilestoneDialog();
    if (state.activeTab === "tasks") openCreateProgressTaskDialog();
    if (state.activeTab === "raw") selectRawFile();
    if (state.activeTab === "equipment") selectCategoryFile("equipment");
    if (state.activeTab === "finance") selectCategoryFile("finance");
    if (state.activeTab === "people") openCreatePersonDialog();
    if (state.activeTab === "tests") openCreateTestDialog();
  });
  elements.searchInput.addEventListener("input", debounce(loadProjects, 250));
  elements.tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      state.activeTab = tab.dataset.tab;
      render();
      if (state.activeTab === "knowledge") {
        loadKnowledge();
      }
      if (state.activeTab === "nodeAlerts") {
        loadMilestones();
      }
      if (state.activeTab === "raw") {
        loadRawFiles();
      }
      if (state.activeTab === "equipment") {
        loadEquipmentData();
      }
      if (state.activeTab === "finance") {
        loadCategoryFiles("finance");
      }
      if (state.activeTab === "tasks") {
        loadProgressTasks();
      }
      if (state.activeTab === "publications") {
        loadPublications();
      }
      if (state.activeTab === "meetings") {
        loadMeetings();
      }
      if (state.activeTab === "people") {
        loadPeople();
      }
      if (state.activeTab === "tests") {
        loadTests();
      }
    });
  });
}

async function checkLogin() {
  try {
    const data = await api("/api/auth/me");
    state.currentUser = data.user;
    renderAuthState();
    await loadProjects();
  } catch (error) {
    state.currentUser = null;
    renderAuthState();
  }
}

async function login(event) {
  event.preventDefault();
  elements.loginError.textContent = "";
  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username: elements.loginUsername.value.trim(),
        password: elements.loginPassword.value,
      }),
    });
    state.currentUser = data.user;
    elements.loginPassword.value = "";
    renderAuthState();
    await loadProjects();
  } catch (error) {
    elements.loginError.textContent = error.message;
  }
}

async function logout() {
  try {
    await api("/api/auth/logout", { method: "POST" });
  } catch (error) {
    // Logout should still clear the local view if the server session is already gone.
  }
  state.currentUser = null;
  state.projects = [];
  state.selectedProject = null;
  renderAuthState();
}

function renderAuthState() {
  const loggedIn = Boolean(state.currentUser);
  document.body.classList.toggle("logged-out", !loggedIn);
  elements.loginView.hidden = loggedIn;
  elements.currentUserLabel.textContent = loggedIn ? `账号：${state.currentUser.display_name || state.currentUser.username}` : "";
  if (!loggedIn) {
    elements.loginUsername.focus();
  }
}

function openDeleteProjectDialog(project) {
  state.projectPendingDeletion = project;
  elements.deleteProjectMessage.textContent = `确认删除项目「${project.name}」吗？`;
  elements.deleteProjectFolderCheckbox.checked = false;
  elements.deleteProjectError.textContent = "";
  elements.deleteProjectDialog.showModal();
}

function closeDeleteProjectDialog() {
  elements.deleteProjectDialog.close();
  state.projectPendingDeletion = null;
}

async function confirmDeleteProject(event) {
  event.preventDefault();
  const project = state.projectPendingDeletion;
  if (!project) return;

  elements.deleteProjectError.textContent = "";
  try {
    await api(`/api/projects/${project.id}`, {
      method: "DELETE",
      body: JSON.stringify({
        delete_folder: elements.deleteProjectFolderCheckbox.checked,
      }),
    });
    if (state.selectedProject?.id === project.id) {
      state.selectedProject = null;
    }
    closeDeleteProjectDialog();
    await loadProjects();
  } catch (error) {
    elements.deleteProjectError.textContent = error.message;
  }
}

function openCreateProjectDialog() {
  state.projectDialogMode = "create";
  elements.projectDialogTitle.textContent = "新建项目";
  elements.projectForm.reset();
  elements.form.status.value = "进行中";
  elements.projectFormError.textContent = "";
  elements.projectDialog.showModal();
  elements.form.name.focus();
}

function openEditProjectDialog() {
  if (!state.selectedProject) return;
  state.projectDialogMode = "edit";
  elements.projectDialogTitle.textContent = "编辑项目信息";
  fillProjectForm(state.selectedProject);
  elements.projectFormError.textContent = "";
  elements.projectDialog.showModal();
  elements.form.name.focus();
}

function closeProjectDialog() {
  elements.projectDialog.close();
}

function openCreateMilestoneDialog() {
  if (!state.selectedProject) return;
  state.milestoneDialogMode = "create";
  state.selectedMilestoneId = null;
  elements.milestoneDialogTitle.textContent = "增加节点";
  elements.milestoneForm.reset();
  elements.milestoneFormFields.status.value = "未开始";
  elements.milestoneFormError.textContent = "";
  elements.milestoneDialog.showModal();
  elements.milestoneFormFields.due_date.focus();
}

function openEditMilestoneDialog(milestone) {
  state.milestoneDialogMode = "edit";
  state.selectedMilestoneId = milestone.id;
  elements.milestoneDialogTitle.textContent = "编辑节点";
  elements.milestoneFormFields.due_date.value = milestone.due_date || "";
  elements.milestoneFormFields.owner.value = milestone.owner || "";
  elements.milestoneFormFields.target.value = milestone.target || "";
  elements.milestoneFormFields.assessment.value = milestone.assessment || "";
  elements.milestoneFormFields.status.value = milestone.status || "未开始";
  elements.milestoneFormFields.note.value = milestone.note || "";
  elements.milestoneFormError.textContent = "";
  elements.milestoneDialog.showModal();
  elements.milestoneFormFields.target.focus();
}

function closeMilestoneDialog() {
  elements.milestoneDialog.close();
}

function openCreateProgressTaskDialog() {
  if (!state.selectedProject) return;
  state.progressTaskDialogMode = "create";
  state.selectedProgressTaskId = null;
  elements.progressTaskDialogTitle.textContent = "增加任务";
  elements.progressTaskForm.reset();
  elements.progressTaskFormFields.progress_percent.value = 0;
  elements.progressTaskFormFields.status.value = "未开始";
  elements.progressTaskFormError.textContent = "";
  elements.progressTaskDialog.showModal();
  elements.progressTaskFormFields.task_name.focus();
}

function openEditProgressTaskDialog(item) {
  state.progressTaskDialogMode = "edit";
  state.selectedProgressTaskId = item.id;
  elements.progressTaskDialogTitle.textContent = "编辑任务";
  elements.progressTaskFormFields.subject_name.value = item.subject_name || "";
  elements.progressTaskFormFields.task_name.value = item.task_name || "";
  elements.progressTaskFormFields.owner.value = item.owner || "";
  elements.progressTaskFormFields.progress_percent.value = item.progress_percent ?? 0;
  elements.progressTaskFormFields.start_date.value = item.start_date || "";
  elements.progressTaskFormFields.end_date.value = item.end_date || "";
  elements.progressTaskFormFields.status.value = item.status || "未开始";
  elements.progressTaskFormFields.progress_note.value = item.progress_note || "";
  elements.progressTaskFormError.textContent = "";
  elements.progressTaskDialog.showModal();
  elements.progressTaskFormFields.task_name.focus();
}

function closeProgressTaskDialog() {
  elements.progressTaskDialog.close();
}

function openCreateEquipmentPlanDialog() {
  if (!state.selectedProject) return;
  state.equipmentPlanDialogMode = "create";
  state.selectedEquipmentPlanId = null;
  elements.equipmentPlanDialogTitle.textContent = "增加规划";
  elements.equipmentPlanForm.reset();
  elements.equipmentPlanFormError.textContent = "";
  elements.equipmentPlanDialog.showModal();
  elements.equipmentPlanFormFields.plan_time.focus();
}

function openEditEquipmentPlanDialog(item) {
  state.equipmentPlanDialogMode = "edit";
  state.selectedEquipmentPlanId = item.id;
  elements.equipmentPlanDialogTitle.textContent = "编辑规划";
  elements.equipmentPlanFormFields.plan_time.value = item.plan_time || "";
  elements.equipmentPlanFormFields.budget.value = item.budget ?? "";
  elements.equipmentPlanFormFields.supplier.value = item.supplier || "";
  elements.equipmentPlanFormFields.closure_material_requirements.value = item.closure_material_requirements || "";
  elements.equipmentPlanFormError.textContent = "";
  elements.equipmentPlanDialog.showModal();
  elements.equipmentPlanFormFields.plan_time.focus();
}

function closeEquipmentPlanDialog() {
  elements.equipmentPlanDialog.close();
}

function openCreatePersonDialog() {
  if (!state.selectedProject) return;
  elements.personForm.reset();
  elements.personFormError.textContent = "";
  elements.personDialog.showModal();
  elements.personFormFields.name.focus();
}

function closePersonDialog() {
  elements.personDialog.close();
}

function openCreateTestDialog() {
  if (!state.selectedProject) return;
  state.testDialogMode = "create";
  state.selectedTestId = null;
  elements.testDialogTitle.textContent = "增加测试项";
  elements.testForm.reset();
  elements.testFormFields.third_party_test.value = "false";
  elements.testFormError.textContent = "";
  elements.testDialog.showModal();
  elements.testFormFields.subject_name.focus();
}

function openEditTestDialog(item) {
  state.testDialogMode = "edit";
  state.selectedTestId = item.id;
  elements.testDialogTitle.textContent = "编辑测试项";
  elements.testFormFields.subject_name.value = item.subject_name || item.name || "";
  elements.testFormFields.metric_name.value = item.metric_name || "";
  elements.testFormFields.expected_midterm_metric.value = item.expected_midterm_metric || "";
  elements.testFormFields.expected_final_metric.value = item.expected_final_metric || "";
  elements.testFormFields.third_party_test.value = item.third_party_test ? "true" : "false";
  elements.testFormFields.test_outline_summary.value = item.test_outline_summary || "";
  elements.testFormError.textContent = "";
  elements.testDialog.showModal();
  elements.testFormFields.subject_name.focus();
}

function closeTestDialog() {
  elements.testDialog.close();
}

function openPublicationDialog(type) {
  if (!state.selectedProject) return;
  state.publicationDialogType = type;
  const isPaper = type === "paper";
  elements.publicationDialogTitle.textContent = isPaper ? "上传论文" : "上传专利/知识产权";
  elements.publicationForm.reset();
  elements.publicationFormFields.titleLabel.textContent = isPaper ? "论文名称" : "专利/知识产权名称";
  elements.publicationFormFields.paperAuthorsField.hidden = !isPaper;
  elements.publicationFormFields.patentApplicationNoField.hidden = isPaper;
  elements.publicationFormFields.patentStatusField.hidden = isPaper;
  elements.publicationFormFields.patentInventorsField.hidden = isPaper;
  elements.publicationFormFields.labelTypeLabel.textContent = isPaper ? "是否唯一标注/第一标注" : "标注/归属说明";
  elements.publicationFormFields.fileLabel.textContent = isPaper ? "论文文件" : "专利书/知识产权文件";
  elements.publicationFormError.textContent = "";
  elements.publicationDialog.showModal();
  elements.publicationFormFields.title.focus();
}

function closePublicationDialog() {
  elements.publicationDialog.close();
}

function openPublicationTargetDialog() {
  if (!state.selectedProject) return;
  elements.publicationTargetFields.paper_target_count.value = Number(state.selectedProject.paper_target_count || 0);
  elements.publicationTargetFields.patent_target_count.value = Number(state.selectedProject.patent_target_count || 0);
  elements.publicationTargetFormError.textContent = "";
  elements.publicationTargetDialog.showModal();
  elements.publicationTargetFields.paper_target_count.focus();
}

function closePublicationTargetDialog() {
  elements.publicationTargetDialog.close();
}

async function savePublicationTargets(event) {
  event.preventDefault();
  if (!state.selectedProject || state.publicationTargetSaving) return;
  const paperTarget = readNonNegativeInt(elements.publicationTargetFields.paper_target_count.value);
  const patentTarget = readNonNegativeInt(elements.publicationTargetFields.patent_target_count.value);

  state.publicationTargetSaving = true;
  elements.publicationTargetFormError.textContent = "";
  try {
    const project = await api(`/api/projects/${state.selectedProject.id}`, {
      method: "PATCH",
      body: JSON.stringify({
        paper_target_count: paperTarget,
        patent_target_count: patentTarget,
      }),
    });
    state.selectedProject = project;
    state.projects = state.projects.map((item) => (item.id === project.id ? project : item));
    closePublicationTargetDialog();
    renderProjectFields();
    renderPublicationsPanel("目标已更新");
  } catch (error) {
    elements.publicationTargetFormError.textContent = error.message;
  } finally {
    state.publicationTargetSaving = false;
  }
}

async function savePublicationForm(event) {
  event.preventDefault();
  if (!state.selectedProject || state.publicationUploading) return;
  const fields = elements.publicationFormFields;
  const file = fields.file.files?.[0];
  const title = fields.title.value.trim();
  if (!title) {
    elements.publicationFormError.textContent = "请填写名称";
    return;
  }
  if (!file) {
    elements.publicationFormError.textContent = "请选择上传文件";
    return;
  }

  const formData = new FormData();
  if (fields.sequence_no.value) formData.append("sequence_no", fields.sequence_no.value);
  formData.append("title", title);
  formData.append("label_type", fields.labelType.value.trim());
  formData.append("note", fields.note.value.trim());
  formData.append("file", file);
  if (state.publicationDialogType === "paper") {
    formData.append("authors", fields.paperAuthors.value.trim());
  } else {
    formData.append("application_no", fields.patentApplicationNo.value.trim());
    formData.append("status", fields.patentStatus.value.trim());
    formData.append("inventors", fields.patentInventors.value.trim());
  }

  state.publicationUploading = true;
  elements.publicationFormError.textContent = "";
  const endpoint = state.publicationDialogType === "paper" ? "papers" : "patents";
  try {
    const response = await fetch(
      withWorkspace(`/api/projects/${state.selectedProject.id}/${endpoint}`),
      {
        method: "POST",
        credentials: "same-origin",
        body: formData,
      }
    );
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "上传失败" }));
      throw new Error(error.detail || "上传失败");
    }
    closePublicationDialog();
    await loadPublications(true, "上传完成");
  } catch (error) {
    elements.publicationFormError.textContent = error.message;
  } finally {
    state.publicationUploading = false;
  }
}

async function savePersonForm(event) {
  event.preventDefault();
  if (!state.selectedProject) return;

  const payload = readPersonForm();
  if (!payload.name) {
    elements.personFormError.textContent = "请填写姓名";
    return;
  }

  try {
    await api(`/api/projects/${state.selectedProject.id}/people`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    closePersonDialog();
    await loadPeople(true, "已增加人员");
  } catch (error) {
    elements.personFormError.textContent = error.message;
  }
}

async function saveProgressTaskForm(event) {
  event.preventDefault();
  if (!state.selectedProject) return;
  const payload = readProgressTaskForm();
  if (!payload.task_name) {
    elements.progressTaskFormError.textContent = "请填写任务名称";
    return;
  }
  try {
    if (state.progressTaskDialogMode === "create") {
      await api(`/api/projects/${state.selectedProject.id}/progress-tasks`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } else {
      await api(`/api/projects/progress-tasks/${state.selectedProgressTaskId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    }
    closeProgressTaskDialog();
    await loadProgressTasks(true, state.progressTaskDialogMode === "create" ? "已增加任务" : "已更新任务");
  } catch (error) {
    elements.progressTaskFormError.textContent = error.message;
  }
}

async function saveEquipmentPlanForm(event) {
  event.preventDefault();
  if (!state.selectedProject) return;
  const payload = readEquipmentPlanForm();
  try {
    if (state.equipmentPlanDialogMode === "create") {
      await api(`/api/projects/${state.selectedProject.id}/equipment-plans`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } else {
      await api(`/api/projects/equipment-plans/${state.selectedEquipmentPlanId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    }
    closeEquipmentPlanDialog();
    await loadEquipmentPlans(true, state.equipmentPlanDialogMode === "create" ? "已增加规划" : "已更新规划");
  } catch (error) {
    elements.equipmentPlanFormError.textContent = error.message;
  }
}

function readEquipmentPlanForm() {
  return {
    plan_time: normalizeText(elements.equipmentPlanFormFields.plan_time.value),
    budget: readOptionalNumber(elements.equipmentPlanFormFields.budget.value),
    supplier: normalizeText(elements.equipmentPlanFormFields.supplier.value),
    closure_material_requirements: normalizeText(elements.equipmentPlanFormFields.closure_material_requirements.value),
  };
}

function readProgressTaskForm() {
  return {
    subject_name: normalizeText(elements.progressTaskFormFields.subject_name.value),
    task_name: elements.progressTaskFormFields.task_name.value.trim(),
    owner: normalizeText(elements.progressTaskFormFields.owner.value),
    start_date: normalizeText(elements.progressTaskFormFields.start_date.value),
    end_date: normalizeText(elements.progressTaskFormFields.end_date.value),
    progress_percent: readNonNegativeInt(elements.progressTaskFormFields.progress_percent.value),
    status: elements.progressTaskFormFields.status.value || "未开始",
    progress_note: normalizeText(elements.progressTaskFormFields.progress_note.value),
  };
}

async function saveTestForm(event) {
  event.preventDefault();
  if (!state.selectedProject) return;
  const payload = readTestForm();
  if (!payload.subject_name) {
    elements.testFormError.textContent = "请填写课题/待测物名称";
    return;
  }

  try {
    if (state.testDialogMode === "create") {
      await api(`/api/projects/${state.selectedProject.id}/tests`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } else {
      await api(`/api/projects/tests/${state.selectedTestId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    }
    closeTestDialog();
    await loadTests(true, state.testDialogMode === "create" ? "已增加测试项" : "已更新测试项");
  } catch (error) {
    elements.testFormError.textContent = error.message;
  }
}

function readTestForm() {
  return {
    subject_name: elements.testFormFields.subject_name.value.trim(),
    metric_name: normalizeText(elements.testFormFields.metric_name.value),
    expected_midterm_metric: normalizeText(elements.testFormFields.expected_midterm_metric.value),
    expected_final_metric: normalizeText(elements.testFormFields.expected_final_metric.value),
    third_party_test: elements.testFormFields.third_party_test.value === "true",
    test_outline_summary: normalizeText(elements.testFormFields.test_outline_summary.value),
  };
}

function readPersonForm() {
  const sequenceValue = elements.personFormFields.sequence_no.value;
  return {
    sequence_no: sequenceValue === "" ? null : Number(sequenceValue),
    name: elements.personFormFields.name.value.trim(),
    organization: normalizeText(elements.personFormFields.organization.value),
    responsibility: normalizeText(elements.personFormFields.responsibility.value),
    id_number: normalizeText(elements.personFormFields.id_number.value),
    email: normalizeText(elements.personFormFields.email.value),
  };
}

async function saveMilestoneForm(event) {
  event.preventDefault();
  if (!state.selectedProject) return;

  const payload = readMilestoneForm();
  if (!payload.target) {
    elements.milestoneFormError.textContent = "请填写节点目标";
    return;
  }

  try {
    if (state.milestoneDialogMode === "create") {
      await api(`/api/projects/${state.selectedProject.id}/milestones`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } else {
      await api(`/api/projects/milestones/${state.selectedMilestoneId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    }
    closeMilestoneDialog();
    await loadMilestones(true);
  } catch (error) {
    elements.milestoneFormError.textContent = error.message;
  }
}

function readMilestoneForm() {
  return {
    due_date: normalizeText(elements.milestoneFormFields.due_date.value),
    owner: normalizeText(elements.milestoneFormFields.owner.value),
    target: elements.milestoneFormFields.target.value.trim(),
    assessment: normalizeText(elements.milestoneFormFields.assessment.value),
    status: elements.milestoneFormFields.status.value || "未开始",
    note: normalizeText(elements.milestoneFormFields.note.value),
  };
}

async function saveProjectForm(event) {
  event.preventDefault();
  elements.projectFormError.textContent = "";

  const payload = readProjectForm();
  if (!payload.name) {
    elements.projectFormError.textContent = "请填写项目名称";
    return;
  }

  try {
    let project;
    if (state.projectDialogMode === "create") {
      project = await api("/api/projects", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } else {
      const current = state.selectedProject;
      if (payload.name !== current.name) {
        project = await api(`/api/projects/${current.id}/rename`, {
          method: "POST",
          body: JSON.stringify({ name: payload.name }),
        });
      }
      project = await api(`/api/projects/${current.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          source: payload.source,
          start_date: payload.start_date,
          end_date: payload.end_date,
          budget: payload.budget,
          partners: payload.partners,
          owner: payload.owner,
          finance_owner: payload.finance_owner,
          technical_contact: payload.technical_contact,
          paper_target_count: payload.paper_target_count,
          patent_target_count: payload.patent_target_count,
          status: payload.status,
          description: payload.description,
        }),
      });
    }
    state.selectedProject = project;
    closeProjectDialog();
    await loadProjects();
  } catch (error) {
    elements.projectFormError.textContent = error.message;
  }
}

function fillProjectForm(project) {
  elements.form.name.value = project.name || "";
  elements.form.source.value = project.source || "";
  elements.form.status.value = project.status || "进行中";
  elements.form.start_date.value = project.start_date || "";
  elements.form.end_date.value = project.end_date || "";
  elements.form.budget.value = project.budget ?? "";
  elements.form.owner.value = project.owner || "";
  elements.form.finance_owner.value = project.finance_owner || "";
  elements.form.technical_contact.value = project.technical_contact || "";
  elements.form.paper_target_count.value = project.paper_target_count ?? 0;
  elements.form.patent_target_count.value = project.patent_target_count ?? 0;
  elements.form.partners.value = project.partners || "";
  elements.form.description.value = project.description || "";
}

function readProjectForm() {
  const budgetValue = elements.form.budget.value;
  return {
    name: elements.form.name.value.trim(),
    source: normalizeText(elements.form.source.value),
    status: elements.form.status.value || "进行中",
    start_date: normalizeText(elements.form.start_date.value),
    end_date: normalizeText(elements.form.end_date.value),
    budget: budgetValue === "" ? null : Number(budgetValue),
    owner: normalizeText(elements.form.owner.value),
    finance_owner: normalizeText(elements.form.finance_owner.value),
    technical_contact: normalizeText(elements.form.technical_contact.value),
    paper_target_count: readNonNegativeInt(elements.form.paper_target_count.value),
    patent_target_count: readNonNegativeInt(elements.form.patent_target_count.value),
    partners: normalizeText(elements.form.partners.value),
    description: normalizeText(elements.form.description.value),
  };
}

function render() {
  renderProjectList();
  renderProjectHeader();
  renderProjectFields();
  renderTabs();
  renderPanel();
}

function renderProjectList() {
  if (state.projects.length === 0) {
    elements.projectList.innerHTML = '<div class="empty-state">暂无项目<br />点击右上角 + 新建</div>';
    return;
  }

  elements.projectList.innerHTML = "";
  state.projects.forEach((project) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `project-item ${state.selectedProject?.id === project.id ? "active" : ""}`;
    button.innerHTML = `
      <span class="project-item-text">
        <strong>${escapeHtml(project.name)}</strong>
        <span>${escapeHtml(project.source || "未填写来源")} · ${escapeHtml(project.status || "未设置状态")}</span>
      </span>
      <span class="project-delete-button" role="button" tabindex="0" title="删除项目" aria-label="删除项目">×</span>
    `;
    button.addEventListener("click", () => {
      state.selectedProject = project;
      render();
    });
    const deleteButton = button.querySelector(".project-delete-button");
    deleteButton.addEventListener("click", (event) => {
      event.stopPropagation();
      openDeleteProjectDialog(project);
    });
    deleteButton.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        event.stopPropagation();
        openDeleteProjectDialog(project);
      }
    });
    elements.projectList.appendChild(button);
  });
}

function renderProjectHeader() {
  const project = state.selectedProject;
  elements.editProjectButton.disabled = !project;
  elements.projectStatus.textContent = project ? project.status || "未设置状态" : "请选择项目";
  elements.projectTitle.textContent = project ? project.name : "本地项目管理";
}

function renderProjectFields() {
  const project = state.selectedProject;
  elements.sourceValue.textContent = displayValue(project?.source);
  elements.startDateValue.textContent = displayValue(project?.start_date);
  elements.endDateValue.textContent = displayValue(project?.end_date);
  elements.budgetValue.textContent = displayBudget(project?.budget);
  elements.partnersValue.textContent = displayValue(project?.partners);
  elements.ownerValue.textContent = displayValue(project?.owner);
  elements.financeOwnerValue.textContent = displayValue(project?.finance_owner);
  elements.technicalContactValue.textContent = displayValue(project?.technical_contact);
}

function renderTabs() {
  elements.tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === state.activeTab);
  });
}

function renderPanel() {
  const config = tabConfig[state.activeTab];
  elements.activeTabLabel.textContent = config.label;
  elements.panelTitle.textContent = config.title;
  elements.panelAddButton.disabled = !state.selectedProject;
  elements.panelAddButton.hidden = !["tasks", "nodeAlerts", "raw", "equipment", "finance", "people", "tests"].includes(state.activeTab);
  elements.panelAddButton.textContent =
    state.activeTab === "raw" || state.activeTab === "equipment" || state.activeTab === "finance"
      ? "上传文件"
      : state.activeTab === "people"
        ? "增加人员"
        : state.activeTab === "tests"
          ? "增加测试项"
          : state.activeTab === "tasks"
            ? "增加任务"
            : "增加节点";

  if (!state.selectedProject) {
    elements.panelContent.innerHTML = '<div class="empty-state">选择或新建一个项目后查看内容</div>';
    return;
  }

  if (state.activeTab === "nodeAlerts") {
    renderMilestonePanel();
    if (state.milestonesLoadedProjectId !== state.selectedProject.id) {
      loadMilestones();
    }
    return;
  }

  if (state.activeTab === "tasks") {
    renderProgressPanel();
    if (state.progressTasksLoadedProjectId !== state.selectedProject.id) {
      loadProgressTasks();
    }
    return;
  }

  if (state.activeTab === "raw") {
    renderRawFilesPanel();
    if (state.rawFilesLoadedProjectId !== state.selectedProject.id) {
      loadRawFiles();
    }
    return;
  }

  if (state.activeTab === "equipment") {
    renderCategoryFilesPanel("equipment");
    if (
      state.equipmentFilesLoadedProjectId !== state.selectedProject.id ||
      state.equipmentPlansLoadedProjectId !== state.selectedProject.id
    ) {
      loadEquipmentData();
    }
    return;
  }

  if (state.activeTab === "finance") {
    renderCategoryFilesPanel("finance");
    if (state.financeFilesLoadedProjectId !== state.selectedProject.id) {
      loadCategoryFiles("finance");
    }
    return;
  }

  if (state.activeTab === "publications") {
    renderPublicationsPanel();
    if (state.publicationsLoadedProjectId !== state.selectedProject.id) {
      loadPublications();
    }
    return;
  }

  if (state.activeTab === "meetings") {
    renderMeetingsPanel();
    if (state.meetingsLoadedProjectId !== state.selectedProject.id) {
      loadMeetings();
    }
    return;
  }

  if (state.activeTab === "people") {
    renderPeoplePanel();
    if (state.peopleLoadedProjectId !== state.selectedProject.id) {
      loadPeople();
    }
    return;
  }

  if (state.activeTab === "tests") {
    renderTestsPanel();
    if (state.testsLoadedProjectId !== state.selectedProject.id) {
      loadTests();
    }
    return;
  }

  if (state.activeTab === "knowledge") {
    renderKnowledgeEditor();
    if (state.knowledgeLoadedProjectId !== state.selectedProject.id) {
      loadKnowledge();
    }
    return;
  }

  const headerCells = config.headers.map((header) => `<th>${header}</th>`).join("");
  elements.panelContent.innerHTML = `
    <table>
      <thead><tr>${headerCells}</tr></thead>
      <tbody>
        <tr>
          <td colspan="${config.headers.length}" class="empty-row">
            ${config.label} 的增删改查接口将在下一步接入
          </td>
        </tr>
      </tbody>
    </table>
  `;
}

function renderPeoplePanel(statusText = "") {
  if (state.people.length === 0) {
    elements.panelContent.innerHTML = `
      <div class="people-toolbar">
        <a class="download-button" href="/api/projects/templates/people.csv">下载 CSV 模版</a>
        <button class="small-button" type="button" id="importPeopleCsvButton">上传 CSV 批量导入</button>
      </div>
      <div class="empty-state">暂无人员信息<br />点击“增加人员”或上传 CSV 批量导入</div>
      <p class="panel-status">${escapeHtml(statusText)}</p>
    `;
    bindPeopleCsvButton();
    return;
  }

  const rows = state.people
    .map(
      (person, index) => `
        <tr>
          <td>${escapeHtml(person.sequence_no ?? index + 1)}</td>
          <td>${escapeHtml(person.name || "-")}</td>
          <td>${escapeHtml(person.organization || "-")}</td>
          <td>${escapeHtml(person.responsibility || "-")}</td>
          <td>${escapeHtml(maskIdNumber(person.id_number))}</td>
          <td>${escapeHtml(person.email || "-")}</td>
        </tr>
      `
    )
    .join("");

  elements.panelContent.innerHTML = `
    <div class="people-toolbar">
      <div class="toolbar-actions">
        <a class="download-button" href="/api/projects/templates/people.csv">下载 CSV 模版</a>
        <button class="small-button" type="button" id="importPeopleCsvButton">上传 CSV 批量导入</button>
      </div>
      <span>CSV 表头：序号, 姓名, 单位, 负责内容, 身份证号, 邮件</span>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>序号</th>
            <th>姓名</th>
            <th>单位</th>
            <th>负责内容</th>
            <th>身份证号</th>
            <th>邮件</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
    <p class="panel-status">${escapeHtml(statusText)}</p>
  `;
  bindPeopleCsvButton();
}

function bindPeopleCsvButton() {
  const button = document.querySelector("#importPeopleCsvButton");
  if (!button) return;
  button.addEventListener("click", selectPeopleCsv);
}

function selectPeopleCsv() {
  if (!state.selectedProject) return;
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".csv,text/csv";
  input.addEventListener("change", () => {
    const file = input.files?.[0];
    if (file) uploadPeopleCsv(file);
  });
  input.click();
}

async function uploadPeopleCsv(file) {
  if (!state.selectedProject) return;
  renderPeoplePanel("导入中...");
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await fetch(
      withWorkspace(`/api/projects/${state.selectedProject.id}/people/import-csv`),
      {
        method: "POST",
        credentials: "same-origin",
        body: formData,
      }
    );
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "导入失败" }));
      throw new Error(error.detail || "导入失败");
    }
    const result = await response.json();
    await loadPeople(true, `已导入 ${result.created} 条人员信息`);
  } catch (error) {
    renderPeoplePanel(error.message);
  }
}

async function loadPeople(force = false, statusText = "") {
  if (!state.selectedProject) return;
  if (!force && state.peopleLoadedProjectId === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/people`);
    if (state.selectedProject?.id !== projectId) return;
    state.people = data.items || [];
    state.peopleLoadedProjectId = projectId;
    if (state.activeTab === "people") renderPeoplePanel(statusText);
  } catch (error) {
    renderPeoplePanel(error.message);
  }
}

function renderTestsPanel(statusText = "") {
  const rows = state.tests
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.subject_name || item.name || "-")}</td>
          <td>${escapeHtml(item.metric_name || "-")}</td>
          <td>${escapeHtml(item.expected_midterm_metric || "-")}</td>
          <td>${escapeHtml(item.expected_final_metric || "-")}</td>
          <td>${item.third_party_test ? "是" : "否"}</td>
          <td>${escapeHtml(item.test_outline_summary || "-")}</td>
          <td><button class="small-button edit-test-button" type="button" data-test-id="${item.id}">编辑</button></td>
        </tr>
      `
    )
    .join("") || '<tr><td colspan="7" class="empty-row">暂无测试项</td></tr>';

  elements.panelContent.innerHTML = `
    <div class="people-toolbar">
      <div class="toolbar-actions">
        <a class="download-button" href="/api/projects/templates/tests.csv">下载 CSV 模版</a>
        <button class="small-button" type="button" id="importTestsCsvButton">上传 CSV 批量导入</button>
      </div>
      <span>CSV 表头：课题/待测物名称, 指标名称, 预期中期指标, 预期完成指标, 是否第三方测试, 测试大纲缩略版</span>
    </div>
    <div class="table-wrap">
      <table class="test-table">
        <thead>
          <tr>
            <th>课题/待测物名称</th>
            <th>指标名称</th>
            <th>预期中期指标</th>
            <th>预期完成指标</th>
            <th>是否第三方测试</th>
            <th>测试大纲缩略版</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
    <p class="panel-status">${escapeHtml(statusText)}</p>
  `;

  document.querySelector("#importTestsCsvButton")?.addEventListener("click", selectTestsCsv);
  document.querySelectorAll(".edit-test-button").forEach((button) => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.testId);
      const item = state.tests.find((test) => test.id === id);
      if (item) openEditTestDialog(item);
    });
  });
}

function selectTestsCsv() {
  if (!state.selectedProject) return;
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".csv,text/csv";
  input.addEventListener("change", () => {
    const file = input.files?.[0];
    if (file) uploadTestsCsv(file);
  });
  input.click();
}

async function uploadTestsCsv(file) {
  if (!state.selectedProject) return;
  renderTestsPanel("导入中...");
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await fetch(
      withWorkspace(`/api/projects/${state.selectedProject.id}/tests/import-csv`),
      {
        method: "POST",
        credentials: "same-origin",
        body: formData,
      }
    );
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "导入失败" }));
      throw new Error(error.detail || "导入失败");
    }
    const result = await response.json();
    await loadTests(true, `已导入 ${result.created} 条测试项`);
  } catch (error) {
    renderTestsPanel(error.message);
  }
}

async function loadTests(force = false, statusText = "") {
  if (!state.selectedProject) return;
  if (!force && state.testsLoadedProjectId === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/tests`);
    if (state.selectedProject?.id !== projectId) return;
    state.tests = data.items || [];
    state.testsLoadedProjectId = projectId;
    if (state.activeTab === "tests") renderTestsPanel(statusText);
  } catch (error) {
    renderTestsPanel(error.message);
  }
}

function renderProgressPanel(statusText = "") {
  const periods = buildProgressPeriods();
  const headerCells = periods.map((period) => `<th>${escapeHtml(period.label)}</th>`).join("");
  const rows = state.progressTasks
    .map((item) => {
      const cells = periods.map((period) => renderProgressCell(item, period)).join("");
      return `
        <tr>
          <td>${escapeHtml(item.subject_name || "-")}</td>
          <td>${escapeHtml(item.task_name || "-")}</td>
          <td>${escapeHtml(item.owner || "-")}</td>
          <td>${escapeHtml(item.progress_percent ?? 0)}%</td>
          <td>${escapeHtml(item.progress_note || "-")}</td>
          ${cells}
          <td><button class="small-button edit-progress-task-button" type="button" data-task-id="${item.id}">编辑</button></td>
        </tr>
      `;
    })
    .join("") || `<tr><td colspan="${periods.length + 6}" class="empty-row">暂无总体进展任务</td></tr>`;

  elements.panelContent.innerHTML = `
    <div class="progress-toolbar">
      <div class="toolbar-actions">
        <button class="small-button ${state.progressScale === "month" ? "active-toggle" : ""}" type="button" id="progressMonthButton">月度</button>
        <button class="small-button ${state.progressScale === "quarter" ? "active-toggle" : ""}" type="button" id="progressQuarterButton">季度</button>
      </div>
      <div class="progress-legend">
        <span><i class="legend-box status-not-started"></i>待开始</span>
        <span><i class="legend-box status-in-progress"></i>开始/进行中</span>
        <span><i class="legend-box status-warning"></i>进展预警</span>
        <span><i class="legend-box status-delayed"></i>已延期须重点关注</span>
        <span class="current-marker">▼ 当前时间</span>
      </div>
    </div>
    <div class="table-wrap progress-table-wrap">
      <table class="progress-table">
        <thead>
          <tr>
            <th>课题名称</th>
            <th>任务名称</th>
            <th>负责人</th>
            <th>完成进度</th>
            <th>当前进展描述</th>
            ${headerCells}
            <th>操作</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
    <p class="panel-status">${escapeHtml(statusText)}</p>
  `;

  document.querySelector("#progressMonthButton")?.addEventListener("click", () => {
    state.progressScale = "month";
    renderProgressPanel();
  });
  document.querySelector("#progressQuarterButton")?.addEventListener("click", () => {
    state.progressScale = "quarter";
    renderProgressPanel();
  });
  document.querySelectorAll(".edit-progress-task-button").forEach((button) => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.taskId);
      const item = state.progressTasks.find((task) => task.id === id);
      if (item) openEditProgressTaskDialog(item);
    });
  });
}

function buildProgressPeriods() {
  const project = state.selectedProject || {};
  const today = new Date();
  const start = state.progressScale === "month" ? new Date(today.getFullYear(), today.getMonth(), 1) : parseDate(project.start_date) || today;
  const end = state.progressScale === "month" ? addMonths(start, 10) : parseDate(project.end_date) || addMonths(start, 11);
  const periods = [];
  const cursor = new Date(start.getFullYear(), start.getMonth(), 1);
  const endCursor = new Date(end.getFullYear(), end.getMonth(), 1);
  while (cursor <= endCursor && periods.length < 60) {
    if (state.progressScale === "quarter") {
      const quarter = Math.floor(cursor.getMonth() / 3) + 1;
      const qStart = new Date(cursor.getFullYear(), (quarter - 1) * 3, 1);
      const qEnd = new Date(cursor.getFullYear(), quarter * 3, 0);
      periods.push({ start: qStart, end: qEnd, label: `${cursor.getFullYear()} Q${quarter}` });
      cursor.setMonth(cursor.getMonth() + 3);
    } else {
      periods.push({
        start: new Date(cursor),
        end: new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0),
        label: `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, "0")}`,
      });
      cursor.setMonth(cursor.getMonth() + 1);
    }
  }
  return periods;
}

function renderProgressCell(item, period) {
  const taskStart = parseDate(item.start_date);
  const taskEnd = parseDate(item.end_date) || taskStart;
  const active = taskStart && taskEnd && taskStart <= period.end && taskEnd >= period.start;
  const statusClassName = active ? progressStatusClass(item.status) : "";
  const currentClassName = periodContainsToday(period) ? "current-period" : "";
  return `<td class="progress-time-cell ${statusClassName} ${currentClassName}"></td>`;
}

function periodContainsToday(period) {
  const today = new Date();
  const current = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  return current >= period.start && current <= period.end;
}

async function loadProgressTasks(force = false, statusText = "") {
  if (!state.selectedProject) return;
  if (!force && state.progressTasksLoadedProjectId === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/progress-tasks`);
    if (state.selectedProject?.id !== projectId) return;
    state.progressTasks = data.items || [];
    state.progressTasksLoadedProjectId = projectId;
    if (state.activeTab === "tasks") renderProgressPanel(statusText);
  } catch (error) {
    renderProgressPanel(error.message);
  }
}

function renderMeetingsPanel(statusText = "") {
  const today = new Date().toISOString().slice(0, 10);
  const currentDate = document.querySelector("#meetingDateInput")?.value || today;
  const rows = state.meetings
    .map(
      (meeting) => `
        <tr>
          <td>${escapeHtml(meeting.meeting_date || "-")}</td>
          <td>
            ${
              meeting.progress_path
                ? `<a class="download-button" target="_blank" rel="noreferrer" href="${meetingFileUrl(meeting.id, "progress")}">Progress</a>`
                : "-"
            }
          </td>
          <td>
            ${
              meeting.action_items_path
                ? `<a class="download-button" target="_blank" rel="noreferrer" href="${meetingFileUrl(meeting.id, "action-items")}">Action Item</a>`
                : "-"
            }
          </td>
        </tr>
      `
    )
    .join("") || '<tr><td colspan="3" class="empty-row">暂无例会历史</td></tr>';

  elements.panelContent.innerHTML = `
    <div class="meeting-panel">
      <div class="meeting-toolbar">
        <label>
          <span>本次日期</span>
          <input id="meetingDateInput" type="date" value="${escapeHtml(currentDate)}" />
        </label>
        <label>
          <span>上次日期</span>
          <input type="text" value="${escapeHtml(state.lastMeetingDate || "-")}" readonly />
        </label>
        <button id="saveMeetingButton" class="primary-button" type="button" ${state.meetingSaving ? "disabled" : ""}>保存</button>
      </div>
      <div class="meeting-markdown-grid">
        <section>
          <h4>上次 Action Item</h4>
          <div class="markdown-display">${renderMarkdownText(state.lastActionItems || "暂无上次 Action Item")}</div>
        </section>
        <section>
          <h4>本次 Progress</h4>
          <textarea id="meetingProgressEditor" spellcheck="false" placeholder="- 本次进展&#10;- 关键问题&#10;- 下一步计划">${escapeHtml(state.meetingProgress)}</textarea>
        </section>
        <section>
          <h4>本次 Action Item</h4>
          <textarea id="meetingActionItemsEditor" spellcheck="false" placeholder="- [ ] 事项 / 负责人 / 截止时间">${escapeHtml(state.meetingActionItems)}</textarea>
        </section>
      </div>
      <section class="subpanel">
        <h4>例会历史文件</h4>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>日期</th>
                <th>Progress</th>
                <th>Action Item</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </section>
      <p class="panel-status">${escapeHtml(statusText)}</p>
    </div>
  `;

  document.querySelector("#meetingProgressEditor")?.addEventListener("input", (event) => {
    state.meetingProgress = event.target.value;
  });
  document.querySelector("#meetingActionItemsEditor")?.addEventListener("input", (event) => {
    state.meetingActionItems = event.target.value;
  });
  document.querySelector("#saveMeetingButton")?.addEventListener("click", saveMeeting);
}

async function loadMeetings(force = false, statusText = "") {
  if (!state.selectedProject) return;
  if (!force && state.meetingsLoadedProjectId === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/meetings`);
    if (state.selectedProject?.id !== projectId) return;
    state.meetings = data.items || [];
    state.lastMeetingDate = data.last_meeting_date || "";
    state.lastActionItems = data.last_action_items || "";
    state.meetingsLoadedProjectId = projectId;
    if (state.activeTab === "meetings") renderMeetingsPanel(statusText);
  } catch (error) {
    renderMeetingsPanel(error.message);
  }
}

async function saveMeeting() {
  if (!state.selectedProject || state.meetingSaving) return;
  const meetingDate = document.querySelector("#meetingDateInput")?.value;
  if (!meetingDate) {
    renderMeetingsPanel("请填写本次日期");
    return;
  }
  state.meetingSaving = true;
  renderMeetingsPanel("保存中...");
  try {
    await api(`/api/projects/${state.selectedProject.id}/meetings`, {
      method: "POST",
      body: JSON.stringify({
        meeting_date: meetingDate,
        progress: state.meetingProgress,
        action_items: state.meetingActionItems,
      }),
    });
    state.meetingProgress = "";
    state.meetingActionItems = "";
    state.meetingsLoadedProjectId = null;
    state.meetingSaving = false;
    await loadMeetings(true, "已保存例会记录");
  } catch (error) {
    state.meetingSaving = false;
    renderMeetingsPanel(error.message);
  }
}

function renderRawFilesPanel(statusText = "") {
  renderFileListPanel({
    files: state.rawFiles,
    emptyLabel: "暂无项目文档",
    emptyHint: "点击“上传文件”添加任务书、预算书或合同等资料",
    statusText,
  });
}

function renderCategoryFilesPanel(type, statusText = "") {
  const config = categoryFileConfig(type);
  if (type === "equipment") {
    renderEquipmentPanel(statusText);
    return;
  }
  renderFileListPanel({
    files: config.files,
    emptyLabel: `暂无${config.label}文件`,
    emptyHint: "点击“上传文件”添加资料",
    statusText,
  });
}

function renderEquipmentPanel(statusText = "") {
  const planRows = state.equipmentPlans
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.plan_time || "-")}</td>
          <td>${escapeHtml(displayBudget(item.budget))}</td>
          <td>${escapeHtml(item.supplier || "-")}</td>
          <td>${escapeHtml(item.closure_material_requirements || "-")}</td>
          <td><button class="small-button edit-equipment-plan-button" type="button" data-plan-id="${item.id}">编辑</button></td>
        </tr>
      `
    )
    .join("") || '<tr><td colspan="5" class="empty-row">暂无设备/IP/流片规划</td></tr>';

  const filesHtml = renderFileListHtml({
    files: state.equipmentFiles,
    emptyLabel: "暂无合同和技术闭环相关材料",
    emptyHint: "点击“上传文件”添加合同、闭环证明或技术资料",
  });

  elements.panelContent.innerHTML = `
    <section class="panel-section">
      <div class="section-title-row">
        <h4>设备/IP/流片规划</h4>
        <button class="small-button" type="button" id="addEquipmentPlanButton">增加规划</button>
      </div>
      <div class="table-wrap">
        <table class="equipment-plan-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>预算</th>
              <th>供应商</th>
              <th>闭环材料要求</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>${planRows}</tbody>
        </table>
      </div>
    </section>
    <section class="panel-section">
      <div class="section-title-row">
        <h4>合同和技术闭环相关材料</h4>
      </div>
      ${filesHtml}
    </section>
    <p class="panel-status">${escapeHtml(statusText)}</p>
  `;

  document.querySelector("#addEquipmentPlanButton")?.addEventListener("click", openCreateEquipmentPlanDialog);
  document.querySelectorAll(".edit-equipment-plan-button").forEach((button) => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.planId);
      const item = state.equipmentPlans.find((plan) => plan.id === id);
      if (item) openEditEquipmentPlanDialog(item);
    });
  });
}

function renderFileListPanel({ files, emptyLabel, emptyHint, statusText = "" }) {
  const content = renderFileListHtml({ files, emptyLabel, emptyHint });
  elements.panelContent.innerHTML = `
    ${content}
    <p class="panel-status">${escapeHtml(statusText)}</p>
  `;
}

function renderFileListHtml({ files, emptyLabel, emptyHint }) {
  if (files.length === 0) {
    return `
      <div class="empty-state">${escapeHtml(emptyLabel)}<br />${escapeHtml(emptyHint)}</div>
    `;
  }

  const rows = files
    .map(
      (file) => `
        <tr>
          <td>${escapeHtml(file.title || file.original_filename || "-")}</td>
          <td>${escapeHtml(file.file_type || "-")}</td>
          <td>${formatFileSize(file.file_size)}</td>
          <td>${escapeHtml(formatDateTime(file.created_at))}</td>
          <td>
            <a class="download-button" href="${downloadUrl(file.id)}">下载</a>
          </td>
        </tr>
      `
    )
    .join("");

  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>文件名称</th>
            <th>类型</th>
            <th>大小</th>
            <th>上传时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function categoryFileConfig(type) {
  if (type === "equipment") {
    return {
      label: "设备/IP/流片",
      endpoint: "equipment-files",
      files: state.equipmentFiles,
      uploadingKey: "equipmentFileUploading",
      loadedKey: "equipmentFilesLoadedProjectId",
      setter: (items) => {
        state.equipmentFiles = items;
      },
      renderer: renderCategoryFilesPanel,
    };
  }
  return {
    label: "财务情况更新",
    endpoint: "finance-files",
    files: state.financeFiles,
    uploadingKey: "financeFileUploading",
    loadedKey: "financeFilesLoadedProjectId",
    setter: (items) => {
      state.financeFiles = items;
    },
    renderer: renderCategoryFilesPanel,
  };
}

function renderPublicationsPanel(statusText = "") {
  elements.panelContent.innerHTML = `
    ${renderPublicationSummary()}
    <div class="publication-toolbar">
      <button class="small-button" type="button" id="uploadPaperButton">上传论文</button>
      <button class="small-button" type="button" id="uploadPatentButton">上传专利/知识产权</button>
    </div>
    ${renderPapersTable()}
    ${renderPatentsTable()}
    <p class="panel-status">${escapeHtml(statusText)}</p>
  `;

  document.querySelector("#editPublicationTargetsButton")?.addEventListener("click", openPublicationTargetDialog);
  document.querySelector("#uploadPaperButton")?.addEventListener("click", () => openPublicationDialog("paper"));
  document.querySelector("#uploadPatentButton")?.addEventListener("click", () => openPublicationDialog("patent"));
  document.querySelectorAll(".delete-paper-button").forEach((button) => {
    button.addEventListener("click", () => deletePublication("paper", Number(button.dataset.paperId)));
  });
  document.querySelectorAll(".delete-patent-button").forEach((button) => {
    button.addEventListener("click", () => deletePublication("patent", Number(button.dataset.patentId)));
  });
}

function renderPublicationSummary() {
  const paperDone = state.papers.length;
  const patentDone = state.patents.length;
  const paperTarget = Number(state.selectedProject?.paper_target_count || 0);
  const patentTarget = Number(state.selectedProject?.patent_target_count || 0);
  const totalDone = paperDone + patentDone;
  const totalTarget = paperTarget + patentTarget;
  const totalPercent = progressPercent(totalDone, totalTarget);
  return `
    <section class="publication-summary">
      <div class="summary-cell">
        <span>论文目标</span>
        <strong>${paperDone}/${paperTarget || "-"}</strong>
        <small>${progressLabel(paperDone, paperTarget)}</small>
      </div>
      <div class="summary-cell">
        <span>专利目标</span>
        <strong>${patentDone}/${patentTarget || "-"}</strong>
        <small>${progressLabel(patentDone, patentTarget)}</small>
      </div>
      <div class="summary-cell">
        <span>合计完成</span>
        <strong>${totalDone}/${totalTarget || "-"}</strong>
        <small>${totalTarget > 0 ? `${totalPercent}%` : "未设置目标"}</small>
      </div>
      <div class="summary-progress" aria-label="论文专利完成比例">
        <span style="width: ${totalPercent}%;"></span>
      </div>
      <button class="small-button" type="button" id="editPublicationTargetsButton">编辑目标</button>
    </section>
  `;
}

function renderPapersTable() {
  const rows = state.papers
    .map(
      (paper, index) => `
        <tr>
          <td>${escapeHtml(paper.sequence_no ?? index + 1)}</td>
          <td>${escapeHtml(paper.title || "-")}</td>
          <td>${escapeHtml(paper.authors || "-")}</td>
          <td>${escapeHtml(paper.label_type || "-")}</td>
          <td>${escapeHtml(paper.note || "-")}</td>
          <td>
            <div class="row-actions">
              ${paper.pdf_path ? `<a class="download-button" href="${paperDownloadUrl(paper.id)}">下载</a>` : ""}
              <button class="small-button danger-inline-button delete-paper-button" type="button" data-paper-id="${paper.id}">删除</button>
            </div>
          </td>
        </tr>
      `
    )
    .join("") || '<tr><td colspan="6" class="empty-row">暂无论文记录</td></tr>';
  return `
    <section class="subpanel">
      <h4>论文</h4>
      <div class="table-wrap">
        <table class="publication-table paper-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>名称</th>
              <th>作者列表</th>
              <th>是否是唯一标注/第一标注</th>
              <th>备注</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </section>
  `;
}

function renderPatentsTable() {
  const rows = state.patents
    .map(
      (patent, index) => `
        <tr>
          <td>${escapeHtml(patent.sequence_no ?? index + 1)}</td>
          <td>${escapeHtml(patent.title || "-")}</td>
          <td>${escapeHtml(patent.application_no || "-")}</td>
          <td>${escapeHtml(patent.status || "-")}</td>
          <td>${escapeHtml(patent.inventors || "-")}</td>
          <td>${escapeHtml(patent.label_type || "-")}</td>
          <td>${escapeHtml(patent.note || "-")}</td>
          <td>
            <div class="row-actions">
              ${patent.pdf_path ? `<a class="download-button" href="${patentDownloadUrl(patent.id)}">下载</a>` : ""}
              <button class="small-button danger-inline-button delete-patent-button" type="button" data-patent-id="${patent.id}">删除</button>
            </div>
          </td>
        </tr>
      `
    )
    .join("") || '<tr><td colspan="8" class="empty-row">暂无专利/知识产权记录</td></tr>';
  return `
    <section class="subpanel">
      <h4>专利</h4>
      <div class="table-wrap">
        <table class="publication-table patent-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>名称</th>
              <th>专利号</th>
              <th>专利状态</th>
              <th>发明人列表</th>
              <th>标注/归属说明</th>
              <th>备注</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </section>
  `;
}

async function deletePublication(type, id) {
  if (!id) return;
  const label = type === "paper" ? "论文" : "专利";
  const confirmed = window.confirm(`确认删除这条${label}记录吗？附件文件会保留在项目目录中。`);
  if (!confirmed) return;
  const endpoint = type === "paper" ? "papers" : "patents";
  try {
    await api(`/api/projects/${endpoint}/${id}`, { method: "DELETE" });
    await loadPublications(true, `已删除${label}记录`);
  } catch (error) {
    renderPublicationsPanel(error.message);
  }
}

async function loadPublications(force = false, statusText = "") {
  if (!state.selectedProject) return;
  if (!force && state.publicationsLoadedProjectId === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const [papers, patents] = await Promise.all([
      api(`/api/projects/${projectId}/papers`),
      api(`/api/projects/${projectId}/patents`),
    ]);
    if (state.selectedProject?.id !== projectId) return;
    state.papers = papers.items || [];
    state.patents = patents.items || [];
    state.publicationsLoadedProjectId = projectId;
    if (state.activeTab === "publications") renderPublicationsPanel(statusText);
  } catch (error) {
    renderPublicationsPanel(error.message);
  }
}

function selectRawFile() {
  if (!state.selectedProject || state.rawFileUploading) return;
  const input = document.createElement("input");
  input.type = "file";
  input.addEventListener("change", () => {
    const file = input.files?.[0];
    if (file) uploadRawFile(file);
  });
  input.click();
}

function selectCategoryFile(type) {
  if (!state.selectedProject) return;
  const config = categoryFileConfig(type);
  if (state[config.uploadingKey]) return;
  const input = document.createElement("input");
  input.type = "file";
  input.addEventListener("change", () => {
    const file = input.files?.[0];
    if (file) uploadCategoryFile(type, file);
  });
  input.click();
}

async function uploadRawFile(file) {
  if (!state.selectedProject) return;
  state.rawFileUploading = true;
  renderRawFilesPanel("上传中...");
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await fetch(
      withWorkspace(`/api/projects/${state.selectedProject.id}/raw-files`),
      {
        method: "POST",
        credentials: "same-origin",
        body: formData,
      }
    );
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "上传失败" }));
      throw new Error(error.detail || "上传失败");
    }
    await loadRawFiles(true, "上传完成");
  } catch (error) {
    renderRawFilesPanel(error.message);
  } finally {
    state.rawFileUploading = false;
  }
}

async function uploadCategoryFile(type, file) {
  if (!state.selectedProject || !file) return;
  const config = categoryFileConfig(type);
  state[config.uploadingKey] = true;
  renderCategoryFilesPanel(type, "上传中...");
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await fetch(
      withWorkspace(`/api/projects/${state.selectedProject.id}/${config.endpoint}`),
      {
        method: "POST",
        credentials: "same-origin",
        body: formData,
      }
    );
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "上传失败" }));
      throw new Error(error.detail || "上传失败");
    }
    await loadCategoryFiles(type, true, "上传完成");
  } catch (error) {
    renderCategoryFilesPanel(type, error.message);
  } finally {
    state[config.uploadingKey] = false;
  }
}

async function loadRawFiles(force = false, statusText = "") {
  if (!state.selectedProject) return;
  if (!force && state.rawFilesLoadedProjectId === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/raw-files`);
    if (state.selectedProject?.id !== projectId) return;
    state.rawFiles = data.items || [];
    state.rawFilesLoadedProjectId = projectId;
    if (state.activeTab === "raw") renderRawFilesPanel(statusText);
  } catch (error) {
    renderRawFilesPanel(error.message);
  }
}

async function loadCategoryFiles(type, force = false, statusText = "") {
  if (!state.selectedProject) return;
  const config = categoryFileConfig(type);
  if (!force && state[config.loadedKey] === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/${config.endpoint}`);
    if (state.selectedProject?.id !== projectId) return;
    config.setter(data.items || []);
    state[config.loadedKey] = projectId;
    if (state.activeTab === type) renderCategoryFilesPanel(type, statusText);
  } catch (error) {
    renderCategoryFilesPanel(type, error.message);
  }
}

async function loadEquipmentData(force = false, statusText = "") {
  await Promise.all([
    loadEquipmentPlans(force, statusText),
    loadCategoryFiles("equipment", force, statusText),
  ]);
}

async function loadEquipmentPlans(force = false, statusText = "") {
  if (!state.selectedProject) return;
  if (!force && state.equipmentPlansLoadedProjectId === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/equipment-plans`);
    if (state.selectedProject?.id !== projectId) return;
    state.equipmentPlans = data.items || [];
    state.equipmentPlansLoadedProjectId = projectId;
    if (state.activeTab === "equipment") renderCategoryFilesPanel("equipment", statusText);
  } catch (error) {
    renderCategoryFilesPanel("equipment", error.message);
  }
}

function renderMilestonePanel(statusText = "") {
  const milestones = [...state.milestones].sort((a, b) => (a.due_date || "").localeCompare(b.due_date || ""));
  if (milestones.length === 0) {
    elements.panelContent.innerHTML = `
      <div class="empty-state">暂无节点提醒<br />点击“增加节点”创建关键节点</div>
    `;
    return;
  }

  const datedMilestones = milestones.filter((item) => item.due_date);
  const ganttHtml = datedMilestones.length > 0 ? renderGantt(datedMilestones) : '<div class="empty-state compact">填写提醒日期后生成时间轴</div>';
  const rows = milestones
    .map(
      (item) => `
        <tr class="${state.selectedMilestoneId === item.id ? "selected-row" : ""}" data-milestone-id="${item.id}">
          <td>${escapeHtml(item.due_date || "-")}</td>
          <td>${escapeHtml(item.owner || "-")}</td>
          <td>${escapeHtml(item.target || "-")}</td>
          <td>${escapeHtml(item.assessment || "-")}</td>
          <td><span class="status-pill status-${statusClass(item.status)}">${escapeHtml(item.status || "未开始")}</span></td>
          <td><button class="small-button edit-milestone-button" type="button" data-milestone-id="${item.id}">编辑</button></td>
        </tr>
      `
    )
    .join("");

  elements.panelContent.innerHTML = `
    <div class="milestone-panel">
      <div class="gantt-board">${ganttHtml}</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>提醒日期</th>
              <th>负责人</th>
              <th>节点目标</th>
              <th>考核方式</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      <p class="panel-status">${escapeHtml(statusText)}</p>
    </div>
  `;

  document.querySelectorAll(".edit-milestone-button").forEach((button) => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.milestoneId);
      const milestone = state.milestones.find((item) => item.id === id);
      if (milestone) openEditMilestoneDialog(milestone);
    });
  });
}

function renderGantt(milestones) {
  const dates = milestones.map((item) => new Date(item.due_date));
  const minDate = new Date(Math.min(...dates));
  const maxDate = new Date(Math.max(...dates));
  const totalDays = Math.max(1, Math.round((maxDate - minDate) / 86400000));
  const items = milestones
    .map((item) => {
      const offsetDays = Math.max(0, Math.round((new Date(item.due_date) - minDate) / 86400000));
      const left = Math.min(96, Math.max(0, (offsetDays / totalDays) * 96));
      return `
        <div class="gantt-item" style="left: ${left}%;">
          <button class="gantt-dot status-${statusClass(item.status)}" type="button" title="${escapeHtml(item.target)}"></button>
          <div class="gantt-label">
            <strong>${escapeHtml(item.target)}</strong>
            <span>${escapeHtml(item.due_date)} · ${escapeHtml(item.owner || "未分配")}</span>
          </div>
        </div>
      `;
    })
    .join("");
  return `
    <div class="gantt-scale">
      <span>${formatDate(minDate)}</span>
      <span>${formatDate(maxDate)}</span>
    </div>
    <div class="gantt-line">${items}</div>
  `;
}

async function loadMilestones(force = false) {
  if (!state.selectedProject) return;
  if (!force && state.milestonesLoadedProjectId === state.selectedProject.id) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/milestones`);
    if (state.selectedProject?.id !== projectId) return;
    state.milestones = data.items || [];
    state.milestonesLoadedProjectId = projectId;
    if (state.activeTab === "nodeAlerts") renderMilestonePanel();
  } catch (error) {
    renderMilestonePanel(error.message);
  }
}

function renderKnowledgeEditor(statusText = "") {
  const project = state.selectedProject;
  const disabled = !project || state.knowledgeSaving;
  elements.panelContent.innerHTML = `
    <div class="markdown-editor">
      <div class="markdown-toolbar">
        <span class="markdown-path">${escapeHtml(state.knowledgeFilePath || "知识库/知识库.md")}</span>
        <button id="saveKnowledgeButton" class="primary-button" type="button" ${disabled ? "disabled" : ""}>保存 Markdown</button>
      </div>
      <textarea id="knowledgeEditor" spellcheck="false" placeholder="# 项目知识库&#10;&#10;在这里记录项目背景、关键链接、经验总结、问题排查和复用资料。">${escapeHtml(state.knowledgeContent)}</textarea>
      <div class="markdown-footer">
        <span>Markdown 文件保存在当前项目目录下</span>
        <span id="knowledgeStatus">${escapeHtml(statusText)}</span>
      </div>
    </div>
  `;

  const editor = document.querySelector("#knowledgeEditor");
  const saveButton = document.querySelector("#saveKnowledgeButton");
  editor.addEventListener("input", () => {
    state.knowledgeContent = editor.value;
  });
  saveButton.addEventListener("click", saveKnowledge);
}

async function loadKnowledge() {
  if (!state.selectedProject) return;
  const projectId = state.selectedProject.id;
  try {
    const data = await api(`/api/projects/${projectId}/knowledge`);
    if (state.selectedProject?.id !== projectId) return;
    state.knowledgeContent = data.content || "";
    state.knowledgeFilePath = data.file_path || "";
    state.knowledgeLoadedProjectId = projectId;
    if (state.activeTab === "knowledge") {
      renderKnowledgeEditor();
    }
  } catch (error) {
    renderKnowledgeEditor(error.message);
  }
}

async function saveKnowledge() {
  if (!state.selectedProject) return;
  state.knowledgeSaving = true;
  renderKnowledgeEditor("保存中...");
  try {
    const data = await api(`/api/projects/${state.selectedProject.id}/knowledge`, {
      method: "PUT",
      body: JSON.stringify({ content: state.knowledgeContent }),
    });
    state.knowledgeContent = data.content || "";
    state.knowledgeFilePath = data.file_path || "";
    state.knowledgeLoadedProjectId = state.selectedProject.id;
    state.knowledgeSaving = false;
    renderKnowledgeEditor("已保存");
  } catch (error) {
    state.knowledgeSaving = false;
    renderKnowledgeEditor(error.message);
  }
}

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), delay);
  };
}

function normalizeText(value) {
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

function readNonNegativeInt(value) {
  const number = Number(value);
  if (!Number.isFinite(number) || number < 0) return 0;
  return Math.floor(number);
}

function readOptionalNumber(value) {
  if (value === null || value === undefined || String(value).trim() === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function progressPercent(done, target) {
  if (!target) return 0;
  return Math.min(100, Math.round((done / target) * 100));
}

function progressLabel(done, target) {
  if (!target) return "未设置目标";
  return `${progressPercent(done, target)}%`;
}

function parseDate(value) {
  if (!value) return null;
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

function addMonths(date, count) {
  return new Date(date.getFullYear(), date.getMonth() + count, 1);
}

function progressStatusClass(status) {
  const map = {
    未开始: "status-not-started",
    进行中: "status-in-progress",
    已完成: "status-in-progress",
    进展预警: "status-warning",
    已延期: "status-delayed",
  };
  return map[status] || "status-in-progress";
}

function displayValue(value) {
  return value === null || value === undefined || value === "" ? "-" : value;
}

function displayBudget(value) {
  if (value === null || value === undefined || value === "") return "-";
  return Number(value).toLocaleString("zh-CN", {
    maximumFractionDigits: 2,
  });
}

function formatFileSize(value) {
  const size = Number(value || 0);
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function formatDateTime(value) {
  if (!value) return "-";
  return String(value).replace("T", " ").slice(0, 19);
}

function downloadUrl(fileId) {
  return withWorkspace(`/api/projects/files/${fileId}/download`);
}

function paperDownloadUrl(paperId) {
  return withWorkspace(`/api/projects/papers/${paperId}/download`);
}

function patentDownloadUrl(patentId) {
  return withWorkspace(`/api/projects/patents/${patentId}/download`);
}

function meetingFileUrl(meetingId, fileKind) {
  return withWorkspace(`/api/projects/meetings/${meetingId}/${fileKind}`);
}

function maskIdNumber(value) {
  if (!value) return "-";
  const text = String(value);
  if (text.length <= 6) return "XXX";
  return `${text.slice(0, 3)}XXX${text.slice(-2)}`;
}

function statusClass(status) {
  const map = {
    未开始: "todo",
    进行中: "active",
    已完成: "done",
    延期: "late",
  };
  return map[status] || "todo";
}

function formatDate(date) {
  return date.toISOString().slice(0, 10);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMarkdownText(value) {
  const text = escapeHtml(value || "");
  if (!text.trim()) return "";
  return text
    .split("\n")
    .map((line) => {
      if (line.startsWith("# ")) return `<strong>${line.slice(2)}</strong>`;
      if (line.startsWith("- ")) return `<div class="markdown-line">${line}</div>`;
      return `<div class="markdown-line">${line || "&nbsp;"}</div>`;
    })
    .join("");
}

initialize().catch((error) => {
  elements.panelContent.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
});
