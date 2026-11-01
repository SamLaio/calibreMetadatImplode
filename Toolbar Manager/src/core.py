from urllib.parse import quote, urlparse


PROJECT_PLUGINS = (
    'Toolbar Manager', 'Generate Cover', 'Skip ASCII Text Plugin', 'Extract ISBN',
    'Goodreads', 'AZW6 Image Merge', 'Embed Metadata Safe', 'Modify ePub',
    'Find Duplicates', 'EpubSplit', 'Count Pages', 'Send to Kindle',
)


def homepage_for(plugin):
    if plugin is None or not getattr(plugin, 'plugin_path', None):
        return None
    url = getattr(plugin, 'homepage', None)
    if isinstance(url, str):
        try:
            parsed = urlparse(url)
        except ValueError:
            parsed = None
        if parsed is not None and parsed.scheme in ('https', 'http') and parsed.netloc:
            return url
    if plugin.name in PROJECT_PLUGINS:
        return 'https://github.com/SamLaio/calibreMetadatImplode/tree/main/' + quote(plugin.name)
    return None


def change_layout(layout, name, operation):
    items = list(layout)
    if name not in items:
        return tuple(items)
    index = items.index(name)
    if operation == 'remove':
        items.pop(index)
    elif operation in ('left', 'right'):
        target = index + (-1 if operation == 'left' else 1)
        if 0 <= target < len(items):
            items[index], items[target] = items[target], items[index]
    else:
        raise ValueError('不支援的工具列操作。')
    return tuple(items)


def validate_removal(layouts, key, name, action):
    if key in getattr(action, 'dont_remove_from', ()):
        raise ValueError('calibre 不允許從這個位置移除此按鈕。')
    if 'Preferences' not in layouts['toolbar'] and 'Preferences' not in layouts['menubar']:
        raise ValueError('請保留工具列或選單列中的「偏好設定」入口。')
    if 'Location Manager' not in layouts['toolbar-device'] and 'Location Manager' not in layouts['menubar-device']:
        raise ValueError('請保留裝置工具列或裝置選單列中的「位置管理」入口。')
