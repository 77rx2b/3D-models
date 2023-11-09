import * as THREE from 'three';

export class HtmlMixerContext {
  constructor(rendererWebgl, scene, camera) {
    this.updateFcts = [];

    this.update = () => {
      this.updateFcts.forEach(updateFct => updateFct());
    };

    const cssFactor = 1000;
    this.cssFactor = cssFactor;

    this.rendererCss = new THREE.CSS3DRenderer();
    this.rendererWebgl = rendererWebgl;

    const cssCamera = new THREE.PerspectiveCamera(camera.fov, camera.aspect, camera.near * cssFactor, camera.far * cssFactor);
    this.updateFcts.push(() => {
      cssCamera.quaternion.copy(camera.quaternion);

      cssCamera.position
        .copy(camera.position)
        .multiplyScalar(cssFactor);
    });

    this.cssScene = new THREE.Scene();

    this.autoUpdateObjects = true;
    this.updateFcts.push(() => {
      if (!this.autoUpdateObjects) return;
      this.cssScene.traverse(cssObject => {
        if (cssObject instanceof THREE.Scene) return;
        const mixerPlane = cssObject.userData.mixerPlane;
        if (mixerPlane === undefined) return;
        mixerPlane.update();
      });
    });

    this.updateFcts.push((delta, now) => {
      this.rendererCss.render(this.cssScene, cssCamera);
    });
  }
}

export class HtmlMixerPlane {
  constructor(mixerContext, domElement, opts) {
    opts = opts || {};
    opts.elementW = opts.elementW !== undefined ? opts.elementW : 768;
    opts.planeW = opts.planeW !== undefined ? opts.planeW : 1;
    opts.planeH = opts.planeH !== undefined ? opts.planeH : 3 / 4;
    opts.object3d = opts.object3d !== undefined ? opts.object3d : null;
    this.domElement = domElement;
    this.updateFcts = [];

    this.update = () => {
      this.updateFcts.forEach(updateFct => updateFct());
    };

    const planeW = opts.planeW;
    const planeH = opts.planeH;

    let object3d;
    if (opts.object3d === null) {
      const planeMaterial = new THREE.MeshBasicMaterial({
        opacity: 0,
        color: new THREE.Color('black'),
        blending: THREE.NoBlending,
        side: THREE.DoubleSide,
      });
      const geometry = new THREE.PlaneGeometry(opts.planeW, opts.planeH);
      object3d = new THREE.Mesh(geometry, planeMaterial);
    } else {
      object3d = opts.object3d;
    }

    this.object3d = object3d;

    const aspectRatio = planeH / planeW;
    const elementWidth = opts.elementW;
    const elementHeight = elementWidth * aspectRatio;

    this.setDomElement = newDomElement => {
      console.log('setDomElement: newDomElement', newDomElement);
      const oldDomElement = this.domElement;
      if (oldDomElement.parentNode) {
        oldDomElement.parentNode.removeChild(oldDomElement);
      }
      this.domElement = domElement = newDomElement;
      cssObject.element = domElement;
      setDomElementSize();
    };

    function setDomElementSize() {
      domElement.style.width = elementWidth + 'px';
      domElement.style.height = elementHeight + 'px';
    }
    setDomElementSize();

    const cssObject = new THREE.CSS3DObject(domElement);
    this.cssObject = cssObject;
    cssObject.scale.set(1, 1, 1).multiplyScalar(mixerContext.cssFactor / (elementWidth / planeW));
    cssObject.userData.mixerPlane = this;

    this.updateFcts.push(() => {
      object3d.updateMatrixWorld();
      const worldMatrix = object3d.matrixWorld;
      const position = new THREE.Vector3();
      const scale = new THREE.Vector3();
      const quaternion = new THREE.Quaternion();
      worldMatrix.decompose(position, quaternion, scale);

      cssObject.quaternion.copy(quaternion);

      cssObject.position
        .copy(position)
        .multiplyScalar(mixerContext.cssFactor);

      const scaleFactor = elementWidth / (object3d.geometry.parameters.width * scale.x);
      cssObject.scale.set(1, 1, 1).multiplyScalar(mixerContext.cssFactor / scaleFactor);
    });

    object3d.addEventListener('added', event => {
      mixerContext.cssScene.add(cssObject);
    });

    object3d.addEventListener('removed', event => {
      mixerContext.cssScene.remove(cssObject);
    });
  }
}
