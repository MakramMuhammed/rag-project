from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import JSONResponse

import aiofiles

from controllers import (
    DataController,
    ProcessController,
    ProjectController,
)
from helpers.config import Settings, get_settings
from models.ChunkModel import ChunkModel
from models.ProjectModel import ProjectModel
from models.db_schemas import DataChunk
from models.enums import ResponseSignal
from .schemas.data import ProcessRequest


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(
    request: Request,
    project_id: str,
    file: UploadFile,
    settings: Settings = Depends(get_settings),
):
    project_model = ProjectModel(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # Validate uploaded file
    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(
        file=file
    )

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal,
                "message": "File validation failed.",
            },
        )

    project_dir_path = ProjectController().get_project_path(
        project_id=project_id
    )

    file_path, file_id = data_controller.generate_unique_filepath(
        original_filename=file.filename,
        project_id=project_id,
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(
                settings.FILE_DEFAULT_CHUNK_SIZE
            ):
                await f.write(chunk)

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value,
                "message": "Failed to upload file.",
            },
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "message": "File uploaded successfully.",
            "file_id": file_id,
            "project_id": str(project_id),
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request,
    project_id: str,
    process_request: ProcessRequest,
):
    process_controller = ProcessController(
        project_id=project_id
    )

    file_content = process_controller.get_file_content(
        file_id=process_request.file_id
    )

    project_model = ProjectModel(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=process_request.file_id,
        chunk_size=process_request.chunk_size,
        overlap_size=process_request.overlap_size,
        #do_reset = process_request.do_reset
    )

    if not file_chunks:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_PROCESSING_FAILED.value,
                "message": "File processing failed.",
            },
        )

    chunks_response = [
        {
            "page_content": chunk.page_content,
            "metadata": chunk.metadata,
        }
        for chunk in file_chunks
    ]


    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = ChunkModel(
        db_client=request.app.db_client
    )

    # if process_request.do_reset:
    #     chunk_model.delete_chunks_by_project_id(
    #         project_id=project_id
    # )

    no_records = await chunk_model.insert_many_chunks(
        chunks=file_chunks_records
    )

    return {
        "signal": ResponseSignal.FILE_PROCESSING_SUCCESS.value,
        "message": "File processed successfully.",
        "chunks": chunks_response,
        "inserted_records": no_records,
    }