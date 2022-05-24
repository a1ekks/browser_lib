from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse, JSONResponse


from browser_lib.internal_objects import LoadPageTask, PageContent
from utils.helpers import StrHelpers


router = APIRouter()


@router.get('/api/loader_task')
async def loader_task_get(request: Request, load_page_task: LoadPageTask = Depends()):
    page_loader_manager = request.app.state.page_loader_manager
    result = await page_loader_manager.get_page(load_page_task)

    if result:
        if load_page_task.clean:
            result['content'] = StrHelpers.clean_html(result['content'])
        if load_page_task.to_json:
            return result
        else:
            return HTMLResponse(content=result.get('content'), status_code=result.get('status'))
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/api/loader_task')
async def loader_task_post(request: Request, load_page_task: LoadPageTask):
    page_loader_manager = request.app.state.page_loader_manager
    result = await page_loader_manager.get_page(load_page_task)

    if result:
        if load_page_task.clean:
            result['content'] = StrHelpers.clean_html(result['content'])
        return result

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/api/task')
async def set_task(request: Request, load_page_task: LoadPageTask):
    page_loader_manager = request.app.state.page_loader_manager
    result = await page_loader_manager.set_task(load_page_task)

    return result


@router.get('/api/page')
async def page_get(request: Request, params: PageContent = Depends()):
    page_loader_manager = request.app.state.page_loader_manager

    result = await page_loader_manager.cache_client.get_data(params.url, to_dict=True)
    if result:
        content = StrHelpers.clean_html(result['content']) if params.clean else result['content']
        return HTMLResponse(content=content, status_code=result['status'])
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content='Not found')
