from rest_framework.renderers import BaseRenderer

__all__ = [
    'CSVRenderer',
]


class CSVRenderer(BaseRenderer):
    """Custom renderer for CSV files"""

    media_type = "text/csv"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return "\n".join([",".join(line) for line in data])
