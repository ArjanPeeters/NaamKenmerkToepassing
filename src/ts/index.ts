import '@app-styles/main.scss';

import { ClipboardHelper, CsvService } from '@app-utils';
import { MaterialNameForm, MaterialNameUpdate } from '@app-forms';
import { IfcViewerFactory } from './components';

new ClipboardHelper();
new CsvService();
new MaterialNameForm();
new MaterialNameUpdate();

IfcViewerFactory.initialize();
