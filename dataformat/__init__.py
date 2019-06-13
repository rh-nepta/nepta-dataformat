from dataformat.package import DataPackage
from dataformat.attachments import Types as AttachmentTypes
from dataformat.package import FileFlags
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
