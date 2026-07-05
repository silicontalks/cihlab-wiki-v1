from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from app.services.projects import (
    ProjectError,
    create_project,
    create_project_milestone,
    create_project_person,
    create_project_test,
    create_equipment_plan,
    create_progress_task,
    delete_project_paper,
    delete_project_patent,
    delete_project,
    get_project_file_path,
    get_project_meeting_file,
    get_project_meeting_workspace,
    get_project_milestone,
    get_project_knowledge,
    get_project_paper_path,
    get_project_patent_path,
    get_project,
    import_project_people_csv,
    import_project_tests_csv,
    list_equipment_plans,
    list_project_people,
    list_project_papers,
    list_project_patents,
    list_project_tests,
    list_progress_tasks,
    list_project_files_by_category,
    list_raw_files,
    list_project_milestones,
    list_projects,
    rename_project,
    save_project_meeting,
    save_project_paper,
    save_project_patent,
    save_project_knowledge,
    save_project_file_by_category,
    save_raw_file,
    update_equipment_plan,
    update_progress_task,
    update_project_milestone,
    update_project_test,
    update_project,
)


router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    source: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    partners: Optional[str] = None
    owner: Optional[str] = None
    finance_owner: Optional[str] = None
    technical_contact: Optional[str] = None
    paper_target_count: Optional[int] = Field(0, ge=0)
    patent_target_count: Optional[int] = Field(0, ge=0)
    status: Optional[str] = "进行中"
    description: Optional[str] = None


class ProjectUpdateRequest(BaseModel):
    source: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    partners: Optional[str] = None
    owner: Optional[str] = None
    finance_owner: Optional[str] = None
    technical_contact: Optional[str] = None
    paper_target_count: Optional[int] = Field(None, ge=0)
    patent_target_count: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    description: Optional[str] = None


class ProjectRenameRequest(BaseModel):
    name: str = Field(..., min_length=1)


class ProjectDeleteRequest(BaseModel):
    delete_folder: bool = False


class ProjectKnowledgeRequest(BaseModel):
    content: str = ""


class ProjectMeetingRequest(BaseModel):
    meeting_date: str = Field(..., min_length=1)
    progress: str = ""
    action_items: str = ""


class ProgressTaskRequest(BaseModel):
    subject_name: Optional[str] = None
    task_name: str = Field(..., min_length=1)
    owner: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    progress_percent: int = Field(0, ge=0, le=100)
    status: Optional[str] = "未开始"
    progress_note: Optional[str] = None


class ProgressTaskUpdateRequest(BaseModel):
    subject_name: Optional[str] = None
    task_name: Optional[str] = None
    owner: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    progress_note: Optional[str] = None


class EquipmentPlanRequest(BaseModel):
    plan_time: Optional[str] = None
    budget: Optional[float] = None
    supplier: Optional[str] = None
    closure_material_requirements: Optional[str] = None


class EquipmentPlanUpdateRequest(BaseModel):
    plan_time: Optional[str] = None
    budget: Optional[float] = None
    supplier: Optional[str] = None
    closure_material_requirements: Optional[str] = None


class MilestoneRequest(BaseModel):
    due_date: Optional[str] = None
    owner: Optional[str] = None
    target: str = Field(..., min_length=1)
    assessment: Optional[str] = None
    status: Optional[str] = "未开始"
    note: Optional[str] = None


class MilestoneUpdateRequest(BaseModel):
    due_date: Optional[str] = None
    owner: Optional[str] = None
    target: Optional[str] = None
    assessment: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None


class ProjectPersonRequest(BaseModel):
    sequence_no: Optional[int] = None
    name: str = Field(..., min_length=1)
    organization: Optional[str] = None
    responsibility: Optional[str] = None
    id_number: Optional[str] = None
    email: Optional[str] = None


class ProjectTestRequest(BaseModel):
    subject_name: str = Field(..., min_length=1)
    metric_name: Optional[str] = None
    expected_midterm_metric: Optional[str] = None
    expected_final_metric: Optional[str] = None
    third_party_test: bool = False
    test_outline_summary: Optional[str] = None


class ProjectTestUpdateRequest(BaseModel):
    subject_name: Optional[str] = None
    metric_name: Optional[str] = None
    expected_midterm_metric: Optional[str] = None
    expected_final_metric: Optional[str] = None
    third_party_test: Optional[bool] = None
    test_outline_summary: Optional[str] = None


@router.get("/templates/people.csv")
def download_people_csv_template() -> Response:
    content = "\ufeff序号,姓名,单位,负责内容,身份证号,邮件\n1,张三,示例单位,项目协调,110101199001011234,zhangsan@example.com\n"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="people-template.csv"'},
    )


@router.get("/templates/tests.csv")
def download_tests_csv_template() -> Response:
    content = (
        "\ufeff课题/待测物名称,指标名称,预期中期指标,预期完成指标,是否第三方测试,测试大纲缩略版\n"
        "示例芯片A,功耗,中期低于10mW,结题低于5mW,是,室温典型电压下测试静态与动态功耗\n"
    )
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="tests-template.csv"'},
    )


@router.get("")
def read_projects(
    workspace_path: Optional[str] = None,
    q: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
) -> dict:
    return list_projects(_path(workspace_path), q=q, status=status_filter)


@router.post("", status_code=status.HTTP_201_CREATED)
def add_project(payload: ProjectCreateRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return create_project(payload.model_dump(), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}")
def read_project(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return get_project(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{project_id}")
def edit_project(project_id: int, payload: ProjectUpdateRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return update_project(project_id, payload.model_dump(exclude_unset=True), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/rename")
def rename(project_id: int, payload: ProjectRenameRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return rename_project(project_id, payload.name, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{project_id}")
def remove_project(project_id: int, payload: ProjectDeleteRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return delete_project(project_id, payload.delete_folder, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}/knowledge")
def read_project_knowledge(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return get_project_knowledge(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{project_id}/knowledge")
def save_knowledge(project_id: int, payload: ProjectKnowledgeRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return save_project_knowledge(project_id, payload.content, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{project_id}/meetings")
def read_project_meetings(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return get_project_meeting_workspace(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/meetings", status_code=status.HTTP_201_CREATED)
def save_meeting(project_id: int, payload: ProjectMeetingRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return save_project_meeting(
            project_id,
            payload.meeting_date,
            payload.progress,
            payload.action_items,
            _path(workspace_path),
        )
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/meetings/{meeting_id}/{file_kind}")
def read_project_meeting_file(meeting_id: int, file_kind: str, workspace_path: Optional[str] = None) -> Response:
    if file_kind not in {"progress", "action-items"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件类型不存在")
    try:
        file_path, record = get_project_meeting_file(
            meeting_id,
            "progress" if file_kind == "progress" else "action_items",
            _path(workspace_path),
        )
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(
        content=file_path.read_text(encoding="utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'inline; filename="{file_path.name}"'},
    )


@router.get("/{project_id}/milestones")
def read_project_milestones(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_project_milestones(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/milestones", status_code=status.HTTP_201_CREATED)
def add_project_milestone(project_id: int, payload: MilestoneRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return create_project_milestone(project_id, payload.model_dump(), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/milestones/{milestone_id}")
def edit_project_milestone(milestone_id: int, payload: MilestoneUpdateRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return update_project_milestone(milestone_id, payload.model_dump(exclude_unset=True), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}/progress-tasks")
def read_progress_tasks(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_progress_tasks(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/progress-tasks", status_code=status.HTTP_201_CREATED)
def add_progress_task(project_id: int, payload: ProgressTaskRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return create_progress_task(project_id, payload.model_dump(), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/progress-tasks/{task_id}")
def edit_progress_task(task_id: int, payload: ProgressTaskUpdateRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return update_progress_task(task_id, payload.model_dump(exclude_unset=True), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}/equipment-plans")
def read_equipment_plans(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_equipment_plans(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/equipment-plans", status_code=status.HTTP_201_CREATED)
def add_equipment_plan(project_id: int, payload: EquipmentPlanRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return create_equipment_plan(project_id, payload.model_dump(), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/equipment-plans/{plan_id}")
def edit_equipment_plan(plan_id: int, payload: EquipmentPlanUpdateRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return update_equipment_plan(plan_id, payload.model_dump(exclude_unset=True), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}/raw-files")
def read_raw_files(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_raw_files(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/raw-files", status_code=status.HTTP_201_CREATED)
def upload_raw_file(project_id: int, file: UploadFile = File(...), workspace_path: Optional[str] = None) -> dict:
    try:
        return save_raw_file(project_id, file.filename or "未命名文件", file.file, file.content_type, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}/equipment-files")
def read_equipment_files(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_project_files_by_category(project_id, "equipment_files", _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/equipment-files", status_code=status.HTTP_201_CREATED)
def upload_equipment_file(project_id: int, file: UploadFile = File(...), workspace_path: Optional[str] = None) -> dict:
    try:
        return save_project_file_by_category(
            project_id,
            "equipment_files",
            "设备-IP-流片",
            file.filename or "未命名文件",
            file.file,
            file.content_type,
            _path(workspace_path),
        )
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}/finance-files")
def read_finance_files(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_project_files_by_category(project_id, "finance_files", _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/finance-files", status_code=status.HTTP_201_CREATED)
def upload_finance_file(project_id: int, file: UploadFile = File(...), workspace_path: Optional[str] = None) -> dict:
    try:
        return save_project_file_by_category(
            project_id,
            "finance_files",
            "财务情况更新",
            file.filename or "未命名文件",
            file.file,
            file.content_type,
            _path(workspace_path),
        )
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}/papers")
def read_project_papers(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_project_papers(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/papers", status_code=status.HTTP_201_CREATED)
def upload_project_paper(
    project_id: int,
    sequence_no: Optional[int] = Form(None),
    title: str = Form(...),
    authors: Optional[str] = Form(None),
    label_type: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    file: UploadFile = File(...),
    workspace_path: Optional[str] = None,
) -> dict:
    try:
        return save_project_paper(
            project_id,
            {
                "sequence_no": sequence_no,
                "title": title,
                "authors": authors,
                "label_type": label_type,
                "note": note,
            },
            file.filename or "论文文件.pdf",
            file.file,
            file.content_type,
            _path(workspace_path),
        )
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/papers/{paper_id}/download")
def download_project_paper(paper_id: int, workspace_path: Optional[str] = None) -> FileResponse:
    try:
        file_path, record = get_project_paper_path(paper_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=file_path.name,
    )


@router.delete("/papers/{paper_id}")
def delete_paper(paper_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return delete_project_paper(paper_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{project_id}/patents")
def read_project_patents(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_project_patents(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/patents", status_code=status.HTTP_201_CREATED)
def upload_project_patent(
    project_id: int,
    sequence_no: Optional[int] = Form(None),
    title: str = Form(...),
    application_no: Optional[str] = Form(None),
    status_value: Optional[str] = Form(None, alias="status"),
    inventors: Optional[str] = Form(None),
    label_type: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    file: UploadFile = File(...),
    workspace_path: Optional[str] = None,
) -> dict:
    try:
        return save_project_patent(
            project_id,
            {
                "sequence_no": sequence_no,
                "title": title,
                "application_no": application_no,
                "status": status_value,
                "inventors": inventors,
                "label_type": label_type,
                "note": note,
            },
            file.filename or "专利文件.pdf",
            file.file,
            file.content_type,
            _path(workspace_path),
        )
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/patents/{patent_id}/download")
def download_project_patent(patent_id: int, workspace_path: Optional[str] = None) -> FileResponse:
    try:
        file_path, record = get_project_patent_path(patent_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=file_path.name,
    )


@router.delete("/patents/{patent_id}")
def delete_patent(patent_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return delete_project_patent(patent_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/files/{file_id}/download")
def download_project_file(file_id: int, workspace_path: Optional[str] = None) -> FileResponse:
    try:
        file_path, record = get_project_file_path(file_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FileResponse(
        file_path,
        media_type=record.get("mime_type") or "application/octet-stream",
        filename=record.get("original_filename") or record.get("title") or file_path.name,
    )


@router.get("/{project_id}/tests")
def read_project_tests(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_project_tests(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/tests", status_code=status.HTTP_201_CREATED)
def add_project_test(project_id: int, payload: ProjectTestRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return create_project_test(project_id, payload.model_dump(), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/tests/{test_id}")
def edit_project_test(test_id: int, payload: ProjectTestUpdateRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return update_project_test(test_id, payload.model_dump(exclude_unset=True), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{project_id}/tests/import-csv")
def import_project_tests(project_id: int, file: UploadFile = File(...), workspace_path: Optional[str] = None) -> dict:
    try:
        return import_project_tests_csv(project_id, file.filename or "tests.csv", file.file, _path(workspace_path))
    except (ProjectError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{project_id}/people")
def read_project_people(project_id: int, workspace_path: Optional[str] = None) -> dict:
    try:
        return list_project_people(project_id, _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{project_id}/people", status_code=status.HTTP_201_CREATED)
def add_project_person(project_id: int, payload: ProjectPersonRequest, workspace_path: Optional[str] = None) -> dict:
    try:
        return create_project_person(project_id, payload.model_dump(), _path(workspace_path))
    except ProjectError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{project_id}/people/import-csv")
def import_project_people(project_id: int, file: UploadFile = File(...), workspace_path: Optional[str] = None) -> dict:
    try:
        return import_project_people_csv(project_id, file.filename or "people.csv", file.file, _path(workspace_path))
    except (ProjectError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def _path(workspace_path: Optional[str]) -> Optional[Path]:
    return Path(workspace_path) if workspace_path else None
