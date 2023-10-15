import { IfcViewer } from './ifc-viewer';

export class IfcViewerFactory {

    public static initialize(selector = '.ifc-viewer'): void {
        document.querySelectorAll<HTMLElement>(selector)
            .forEach((element) => IfcViewerFactory.createInstance(element, element.dataset));
    }

    public static createInstance(element: HTMLElement, options: any): IfcViewer {
        return new IfcViewer(element, options);
    }

}
