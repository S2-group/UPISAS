pull_image_tasks = {}


def show_progress(line, progress):
    """
    Show task progress (red for download, green for extract).
    Used when pulling images.
    """
    if line['status'] == 'Downloading':
        id = f'[red][Download {line["id"]}]'
    elif line['status'] == 'Extracting':
        id = f'[green][Extract  {line["id"]}]'
    else:
        # skip other statuses
        return
    if id not in pull_image_tasks.keys():
        pull_image_tasks[id] = progress.add_task(f"{id}", total=line['progressDetail']['total'])
    else:
        progress.update(pull_image_tasks[id], completed=line['progressDetail']['current'])
