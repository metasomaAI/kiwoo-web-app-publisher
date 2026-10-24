---
id: scene-authoring
name: Scene Authoring
description: Authoritative Loot contract for making authored DOM, Canvas, Three.js, and Splat scene objects individually selectable in Preview, covering manifest identity, source binding, runtime registration, and adapters
inject: conditional
condition: capability:scene-authoring
depends_on: []
checks: []
clarify_slots: []
schema_version: loot_scene_authoring.v5
content_hash: 3132aeff777bcee5a4cb0352719d7707f2d50b2317f54e0039a9602da8f89596
---

<!-- GENERATED from services.scene_manifest.disclosure; do not edit manually. -->

# Loot Scene Authoring Contract

This contract defines the source and runtime identity that makes authored scene objects individually selectable in Preview. The server compiler is authoritative for static declarations; the Runtime Kit is authoritative for runtime selection proof when that proof is requested.

```json
{
  "authoring_invariants": [
    "Put the manifest as static JSON in the persisted entry HTML; never create, replace, or populate loot-scene-manifest from JavaScript.",
    "For loot_scene_authoring.v5, omit the legacy pickable field; selection_mode owns selectability.",
    "Use loot_scene_authoring.v5 for new works and explicit capability upgrades. When editing an existing v3 or v4 work, preserve its schema version unless the task requires migration and the complete v5 edit_capabilities contract can be supplied.",
    "Declare stable node_id, runtime_symbol, and source_binding_id values in source. IDs match the manifest identifier_contract; file paths belong only in source_path.",
    "For each selectable node, declare edit_capabilities that map supported effects to exact source symbols. Bind pixel-producing render functions, palettes, materials, shaders, or state owners instead of granting an entire file.",
    "Declare immutable node metadata only in the static Manifest; runtime registerNode binds node_id to runtime_ref and may add only an applicable pick_target or probe_points.",
    "For Bundle works, set source_path to the exact HTML/JS module that owns runtime_symbol.",
    "Register the exact runtime reference for every selectable declared node.",
    "Install every created runtime adapter with lootScene.registerAdapter(...).",
    "Give every selectable Three node real normalized probe_points or provide a createThreeRaycastAdapter projectBounds callback; registration alone is not a runtime selection proof.",
    "Use direct or aggregate Three selection only for visible raycastable geometry; lights, cameras, and other non-visual runtime objects must use none or a separate visible proxy pick target.",
    "Keep node and source binding identities stable when editing the same object.",
    "Use aggregate or a bounded proxy for repeated primitives; do not register transient particles.",
    "Every Runtime Component required part uses a distinct existing SceneNode ID. For three-particle-field, parts.root equals root_node_id and parts.points is a different registered THREE.Points descendant; never reuse the root ID for points.",
    "For three-object, component_id equals root_node_id and parts.root equals root_node_id. Material properties are exposed only when optional parts.primary_material resolves to an exclusive material.",
    "For moving Canvas objects, expose current geometry or recompute bounded probe points from current runtime state; never freeze registration-time witnesses.",
    "Canvas geometry is optional and always receives stable node.runtime_ref, including for proxy nodes; its current getBoundingClientRect()-local polygon is recomputed for geometry-backed picking, probing, and highlighting.",
    "Canvas geometry polygons must use native finite numbers, be non-degenerate and non-self-intersecting, and use distinct z_index values for overlapping objects when unambiguous Top1 order is required.",
    "A Canvas probe is only a witness when using hitTest: production hitTest must still resolve the exact runtime object.",
    "Register adapters at scene level; never invent selectable objects for guessed pixel regions.",
    "Treat window.__LOOT_SCENE__ and window.__LOOT_COMPONENTS__ as platform-owned, non-writable globals: read their versioned APIs and call methods, but never assign, replace, or delete either global.",
    "Do not call setManifestHash; the server derives it from the immutable WorkVersion."
  ],
  "bundle_source_path_field": "nodes[].source_path",
  "manifest_element_id": "loot-scene-manifest",
  "minimum_authoring_shape": {
    "identity_join": {
      "manifest_node_id": "runtime registerNode.node_id",
      "manifest_runtime_symbol": "exact source variable owning runtime_ref",
      "manifest_source_binding_id": "stable source owner identity"
    },
    "manifest": {
      "bundle_required_node_fields": [
        "source_path"
      ],
      "conditional_node_fields": {
        "direct_aggregate_none": [
          "selection_proxy_symbol must be absent"
        ],
        "non_dom": [
          "capture_descendants must be false"
        ],
        "non_selectable": [
          "edit_capabilities must be present and empty"
        ],
        "proxy": [
          "selection_proxy_symbol"
        ],
        "selectable": [
          "edit_capabilities must declare at least one effect and its exact source_symbols"
        ],
        "v5_forbidden": [
          "pickable must be absent"
        ]
      },
      "declared_node_fields": [
        "node_id",
        "role",
        "semantic_kind",
        "runtime_kind",
        "runtime_symbol",
        "source_binding_id",
        "source_path",
        "parent_id",
        "dependency_node_ids",
        "capture_descendants",
        "selection_mode",
        "selection_proxy_symbol",
        "edit_capabilities"
      ],
      "editable_effect_values": [
        "remove",
        "hide",
        "property_change",
        "geometry_change",
        "appearance_change"
      ],
      "element_id": "loot-scene-manifest",
      "identifier_contract": {
        "examples": [
          "scene.house",
          "binding.scene.house",
          "player.timeline"
        ],
        "fields": [
          "node_id",
          "parent_id",
          "dependency_node_ids[]",
          "source_binding_id"
        ],
        "invalid_examples": [
          "src/main.js:houseEntity",
          "/scene/house"
        ],
        "pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$",
        "source_path_boundary": "File paths belong only in source_path; never prefix an identity with a source file path."
      },
      "required_node_fields": [
        "node_id",
        "role",
        "runtime_kind",
        "runtime_symbol",
        "source_binding_id",
        "capture_descendants",
        "selection_mode",
        "edit_capabilities"
      ],
      "required_top_level_fields": [
        "schema_version",
        "nodes",
        "selection_contract"
      ],
      "script_type": "application/json",
      "selection_contract": {
        "delivery_note": "Complete scene-authoring is the precision-editing target for every new work. When the task requires semantic selection, missing or invalid required-node proof triggers bounded repair and prevents the Agent from claiming final completion. The saved work remains available to Preview and Post when ordinary code, runtime, and security gates pass; selection proof never disables those user actions.",
        "required_fields": [
          "schema_version",
          "requirement",
          "required_node_ids"
        ],
        "required_shape": "requirement=required requires at least one required_node_id; requirement=optional requires required_node_ids=[]",
        "requirement_values": [
          "required",
          "optional"
        ],
        "schema_version": "selection_contract.v1"
      },
      "selection_mode_values": [
        "direct",
        "aggregate",
        "proxy",
        "none"
      ],
      "source_location": "A single static <script type=\"application/json\" id=\"loot-scene-manifest\"> in the persisted entry HTML. The server compiler reads the entry source before runtime; a script created, replaced, or populated by JavaScript is not a declaration."
    },
    "runtime_registration": {
      "adapter_by_runtime_kind": {
        "canvas": "createCanvasAdapter or createCanvasIdBufferAdapter",
        "dom": "createDomAdapter",
        "splat": "createSplatAdapter",
        "three": "createThreeRaycastAdapter"
      },
      "adapter_registration_pattern": "lootScene.registerAdapter(lootScene.createXAdapter({...})); calling createXAdapter alone does not install the adapter",
      "api": "window.__LOOT_SCENE__.v2",
      "api_ownership": "Platform-owned, non-writable global API. Read window.__LOOT_SCENE__.v2 into a local handle and call its methods; never assign, replace, or delete window.__LOOT_SCENE__.",
      "canvas_adapter_required_inputs": [
        "canvas",
        "at least one retained-object callback from hitTest, contains, or geometry; no single callback is mandatory"
      ],
      "canvas_id_buffer_dynamic_witness": "When the canvas, layout, or object can move, provide probePoints(runtimeRef, node) so Headless proof recomputes the current viewport witness and can scroll the exact target into view before ID-buffer readback.",
      "canvas_id_buffer_required_inputs": [
        "canvas",
        "colorToNodeId"
      ],
      "canvas_retained_selection": {
        "callback_precedence": [
          "hitTest",
          "contains",
          "geometry"
        ],
        "contains_signature": "contains: (runtimeRef, point) => boolean | finite distance",
        "failure_behavior": "Throwing, invalid, non-finite, numeric-string, out-of-bounds, degenerate, or self-intersecting geometry fails closed for that object and never invents a pixel-to-object mapping",
        "geometry_coordinate_space": "CSS-local canvas pixels in the current canvas.getBoundingClientRect() box, not DPR-scaled backing pixels",
        "geometry_runtime_behavior": "Loot performs point-in-polygon selection, returns only the highest z_index overlap, breaks equal z_index ties in favor of later objects() or registration paint order, derives up to five current normalized witnesses when probePoints is absent, and draws an exact SVG polygon highlight; overlapping geometry should expose distinct z_index values when an unambiguous Top1 is required",
        "geometry_signature": "geometry: (runtimeRef, node) => { polygon: [{ x, y }, ...], z_index? } | null",
        "geometry_validation": "polygon is simple, non-degenerate, and non-self-intersecting with 3 to 128 vertices inside the current CSS canvas box; each x and y, and z_index when supplied, is a native finite JavaScript number rather than a numeric string; z_index defaults to 0 when absent",
        "hit_test_signature": "hitTest: (cssX, cssY, point) => registeredRuntimeRef | null",
        "identity_contract": "The geometry callback always receives stable node.runtime_ref, even when a proxy node has separate pick_target or highlight_target; runtimeRef is identity only, while geometry is current rendered state and is recomputed whenever geometry-backed picking, probing, or highlighting is requested",
        "optional_capability": "geometry is one available retained-object capability alongside hitTest and contains; it is not a required renderer choice"
      },
      "register_node_forbidden_manifest_fields": [
        "role",
        "semantic_kind",
        "parent_id",
        "runtime_kind",
        "runtime_symbol",
        "source_binding_id",
        "selection_mode",
        "capture_descendants",
        "pickable"
      ],
      "register_node_optional_fields": [
        "pick_target",
        "probe_points"
      ],
      "register_node_required_fields": [
        "node_id",
        "runtime_ref"
      ],
      "registration_boundary": "The static Manifest is the only declaration of role, semantic_kind, parent_id, runtime_kind, runtime_symbol, source_binding_id, selection_mode, and capture_descendants. Runtime registerNode only joins node_id to runtime_ref, plus pick_target for a declared proxy and probe_points only for a genuinely fixed witness. Never repeat immutable Manifest metadata in registerNode.",
      "splat_selection_proof": "createSplatAdapter must receive objectIdProvider for segmented identity or a real surface-aware hitTest for a monolithic top-level splat. Missing proof fails closed and arbitrary viewport pixels must never resolve to the splat root.",
      "three_adapter_initialization": "Create the adapter only after raycaster, camera, and renderer are initialized.",
      "three_adapter_required_inputs": [
        "raycaster",
        "camera",
        "renderer"
      ],
      "three_selection_proof": {
        "normalized_point_schema": {
          "origin": "top-left of the renderer viewport; the adapter maps it through the actual renderer canvas into the browser viewport",
          "shape": {
            "x": "number in [0,1]",
            "y": "number in [0,1]"
          }
        },
        "project_bounds_signature": "projectBounds: (runtimeRef) => [{ x, y }, ...]",
        "requirement": "Every selectable Three node must expose one to five real hit witnesses through registerNode.probe_points or the adapter's projectBounds(runtimeRef). A registered raycaster without witnesses is not selectable.",
        "three_center_projection_example": "projectBounds: runtimeRef => currentThreeWitnesses(runtimeRef, camera); the helper recomputes bounded visible mesh/bounds centers from current matrixWorld and projects them through the current camera on every call",
        "verification": "Loot maps each renderer-local witness through renderer.domElement, DPR, viewport, and scissor, then runs the production raycast adapter; at least one result must return the same declared node_id.",
        "visible_pick_target": "selection_mode=direct or aggregate requires a visible, raycastable Object3D pick target. Non-visual runtime objects such as lights and cameras must use selection_mode=none, or selection_mode=proxy with a separate visible geometry pick target."
      }
    }
  },
  "new_work_requirement": {
    "authoring_model": {
      "component_modules": "Rendering, interaction, animation, physics, audio, and behavior stay as composable source modules bound to semantic entities; they do not own identity.",
      "renderer_adapter": "One semantic entity may bind one renderer object or an aggregate of primitives. Picking resolves the renderer hit back to the semantic node_id.",
      "resource_refs": "Images, models, audio, shaders, and generated buffers are resources referenced by entity modules, not substitutes for semantic nodes.",
      "runtime_boundary": "The authored page remains the deployable H5 experience. A separate editor, binary scene format, WASM engine, or prefab pipeline is not required.",
      "semantic_entity": "A stable node_id plus parent_id identifies an independently editable concept before any renderer object is created."
    },
    "not_satisfied_by": [
      "region-only delivery",
      "a not_applicable or unknown Agent assessment",
      "one scene root standing in for independently editable concepts"
    ],
    "renderer_role": "DOM, Canvas, Three.js, Splat, and WebGL select an adapter; renderer choice never exempts a new work from semantic authoring.",
    "semantic_granularity": "Every independently editable visible concept is a stable node; repeated particles, instances, landmarks, and post-processing are aggregate/layer nodes.",
    "semantic_scene_tree": "expected_and_terminal_verified_when_task_required",
    "source_of_truth": "Stable semantic scene nodes own rendering, picking, Manifest identity, and SourceBinding from the first candidate."
  },
  "optional_runtime_components": {
    "api": "window.__LOOT_COMPONENTS__.v1",
    "api_ownership": "Platform-owned, non-writable global API. Read window.__LOOT_COMPONENTS__.v1 and call its methods; never assign, replace, or delete window.__LOOT_COMPONENTS__.",
    "asset_boundary": "media asset tokens resolve only through the platform-owned current-render asset resolver; arbitrary URLs, unknown tokens, and mismatched audio/video/image types fail before mutation",
    "availability_source": "runtime_selection_capability_lease.v1.components for the current render identity",
    "availability_states": [
      "unavailable",
      "declared",
      "runtime_verified",
      "degraded"
    ],
    "delivery_effect": "Optional precision-editing enhancement. Absence, non-use, or degradation never creates a Review issue by itself and never blocks Preview or Post.",
    "descriptor_schema_version": "runtime_component_descriptor.v1",
    "kinds": {
      "media-player": {
        "editable_properties": {
          "autoplay": "boolean",
          "controls_visible": "boolean",
          "loop": "boolean",
          "muted": "boolean",
          "playback_rate": "number in [0.25,4]",
          "poster_asset_token": "existing asset token",
          "source_asset_token": "existing asset token",
          "volume": "number in [0,1]"
        },
        "optional_parts": [
          "volume",
          "caption",
          "poster"
        ],
        "required_parts": [
          "root",
          "media",
          "transport",
          "timeline"
        ],
        "runtime_kind": "dom"
      },
      "three-object": {
        "editable_properties": {
          "opacity": "number in [0,1] when primary_material is exclusive",
          "position_x": "finite number",
          "position_y": "finite number",
          "position_z": "finite number",
          "primary_color": "#rrggbb when primary_material is exclusive",
          "rotation_x": "finite number in radians",
          "rotation_y": "finite number in radians",
          "rotation_z": "finite number in radians",
          "scale_x": "finite number",
          "scale_y": "finite number",
          "scale_z": "finite number",
          "visible": "boolean"
        },
        "optional_parts": [
          "primary_material"
        ],
        "required_parts": [
          "root"
        ],
        "runtime_kind": "three"
      },
      "three-particle-field": {
        "editable_properties": {
          "color": "bounded color string",
          "count": "safe integer >= 1",
          "enabled": "boolean",
          "opacity": "number in [0,1]",
          "size": "finite number >= 0",
          "speed": "finite number >= 0",
          "spread": "finite number >= 0"
        },
        "optional_parts": [
          "emitter",
          "interaction_proxy"
        ],
        "required_parts": [
          "root",
          "points"
        ],
        "runtime_kind": "three"
      }
    },
    "media_player_registration": {
      "asset_rule": "Declare source_asset_token or poster_asset_token only when an existing typed asset token is present in task context; never copy a URL into a token property.",
      "executable_example": "const lootScene = window.__LOOT_SCENE__?.v2;\nconst lootComponents = window.__LOOT_COMPONENTS__?.v1;\nif (lootScene && lootComponents) {\n  lootScene.registerNode({ node_id: \"player.main\", runtime_ref: playerRoot });\n  lootScene.registerNode({ node_id: \"player.media\", runtime_ref: mediaElement });\n  lootScene.registerNode({ node_id: \"player.transport\", runtime_ref: transportControls });\n  lootScene.registerNode({ node_id: \"player.timeline\", runtime_ref: timelineControl });\n  lootScene.registerAdapter(lootScene.createDomAdapter({}));\n  lootComponents.registerMediaPlayer({\n    schema_version: \"runtime_component_descriptor.v1\",\n    component_id: \"player.main.component\",\n    root_node_id: \"player.main\",\n    parts: {\n      root: \"player.main\",\n      media: \"player.media\",\n      transport: \"player.transport\",\n      timeline: \"player.timeline\"\n    },\n    properties: {\n      autoplay: false,\n      loop: false,\n      muted: false,\n      volume: 0.8,\n      playback_rate: 1,\n      controls_visible: true\n    }\n  });\n}",
      "registration_order": "Declare and register the root, media, transport, and timeline DOM SceneNodes; install the one scene-level DOM adapter; then registerMediaPlayer with those exact node IDs."
    },
    "operations": [
      "registerComponent",
      "registerMediaPlayer",
      "registerThreeParticleField",
      "registerThreeObject",
      "updateComponentProperties",
      "getComponent",
      "listComponents",
      "unregisterComponent",
      "destroy"
    ],
    "particle_update_contract": "registerThreeParticleField apply_properties returns bounded observable properties and may return one aggregate Three Points runtime ref; replacements are committed only through SceneRegistry.updateNode, invalidate the prior runtime epoch, and never declare per-particle identity",
    "property_update_contract": "updateComponentProperties(component_id, bounded_properties, expected_runtime_epoch); a stale epoch fails before asset resolution or runtime mutation",
    "selection_authority": "Component parts reference existing SceneNode IDs. A declaration does not authorize object selection; the current Capability Lease and production Adapter remain authoritative.",
    "three_object_registration": {
      "executable_example": "const SCENE_MUTATIONS = {\n  \"scene.cabin\": {\n    visible: true,\n    position_x: 0,\n    position_y: 0,\n    position_z: 0,\n    rotation_x: 0,\n    rotation_y: 0,\n    rotation_z: 0,\n    scale_x: 1,\n    scale_y: 1,\n    scale_z: 1,\n    primary_color: \"#ffffff\",\n    opacity: 1\n  }\n};\nconst lootScene = window.__LOOT_SCENE__?.v2;\nconst lootComponents = window.__LOOT_COMPONENTS__?.v1;\nif (lootScene && lootComponents) {\n  lootScene.registerNode({ node_id: \"scene.cabin\", runtime_ref: cabinMesh });\n  lootScene.registerNode({ node_id: \"scene.cabin.material\", runtime_ref: cabinMaterial });\n  lootComponents.registerThreeObject({\n    schema_version: \"runtime_component_descriptor.v1\",\n    component_id: \"scene.cabin\",\n    root_node_id: \"scene.cabin\",\n    parts: { root: \"scene.cabin\", primary_material: \"scene.cabin.material\" },\n    properties: SCENE_MUTATIONS[\"scene.cabin\"]\n  });\n}",
      "material_rule": "Declare primary_material only for one exclusive THREE.Material. Shared material refs intentionally withhold primary_color and opacity while preserving root transforms.",
      "mutation_store": "HTML keeps one pure-literal SCENE_MUTATIONS object in its module. Bundle keeps the same declaration in loot/scene-mutations.js and imports it from business code. Every registered property must already exist at component_id.property_id.",
      "registration_order": "Declare the stable root SceneNode and optional primary material descendant, bind their real Three runtime refs, install the one scene-level Three adapter, then call registerThreeObject with component_id equal to root_node_id and values from SCENE_MUTATIONS. Registration may precede the Host Scene Contract: the component remains pending and exposes no editable properties until binding succeeds."
    },
    "three_particle_field_registration": {
      "availability_effect": "Feature-detect both versioned APIs. If the optional component API is absent, the authored work continues without component registration and Preview/Post behavior is unchanged.",
      "executable_example": "const lootScene = window.__LOOT_SCENE__?.v2;\nconst lootComponents = window.__LOOT_COMPONENTS__?.v1;\nif (lootScene && lootComponents) {\n  // particleRoot is a THREE.Group and particlePoints is its THREE.Points child.\n  lootScene.registerNode({\n    node_id: \"garden.fireflies\",\n    runtime_ref: particleRoot\n  });\n  lootScene.registerNode({\n    node_id: \"garden.fireflies.points\",\n    runtime_ref: particlePoints\n  });\n\n  lootComponents.registerThreeParticleField({\n    schema_version: \"runtime_component_descriptor.v1\",\n    component_id: \"garden.fireflies.field\",\n    root_node_id: \"garden.fireflies\",\n    parts: {\n      root: \"garden.fireflies\",\n      points: \"garden.fireflies.points\"\n    },\n    properties: {\n      size: 0.08,\n      color: \"#dfff32\",\n      opacity: 0.85,\n      enabled: true\n    },\n    apply_properties(updates, { points_runtime_ref }) {\n      const points = points_runtime_ref;\n      if (Object.hasOwn(updates, \"size\")) points.material.size = updates.size;\n      if (Object.hasOwn(updates, \"color\")) points.material.color.set(updates.color);\n      if (Object.hasOwn(updates, \"opacity\")) points.material.opacity = updates.opacity;\n      if (Object.hasOwn(updates, \"enabled\")) points.visible = updates.enabled;\n      points.material.needsUpdate = true;\n      return {\n        properties: {\n          size: Number(points.material.size),\n          color: `#${points.material.color.getHexString()}`,\n          opacity: Number(points.material.opacity),\n          enabled: Boolean(points.visible)\n        },\n        points_runtime_ref: points\n      };\n    }\n  });\n}",
      "input_shape": {
        "apply_properties": "(updates, { points_runtime_ref }) => ({ properties: full_observable_state, points_runtime_ref? })",
        "component_id": "stable bounded component ID",
        "parts": {
          "points": "a distinct registered descendant SceneNode ID whose runtime_ref is THREE.Points",
          "root": "the same SceneNode ID as root_node_id"
        },
        "properties": "a bounded subset of count, size, color, opacity, speed, spread, and enabled that apply_properties can mutate and faithfully report",
        "root_node_id": "existing registered Three root SceneNode ID",
        "schema_version": "runtime_component_descriptor.v1"
      },
      "registration_order": "Declare root/points ancestry only in the static Manifest. At runtime, bind the root SceneNode first with node_id plus runtime_ref, then bind its points descendant the same way, then call registerThreeParticleField after both references resolve in window.__LOOT_SCENE__.v2.",
      "round_trip_contract": "Registration immediately invokes apply_properties with the initial properties. Each callback applies the updates to the supplied runtime object and returns the full observable state: every previously accepted property plus every current update with the exact resulting values. Declare only properties the callback can round-trip.",
      "scene_node_structure": "root and points are two distinct existing runtime_kind=three SceneNodes; parts.root equals root_node_id, and the points node reaches root through its parent_id ancestry. The points node runtime_ref is a THREE.Points object. The component root is structural and need not be separately selectable; a non-raycastable THREE.Group root uses selection_mode=none unless it has a separate visible proxy pick target.",
      "selection_prerequisite": "Component registration does not install object selection. Install exactly one scene-level createThreeRaycastAdapter whose dynamic projectBounds samples current Points vertices and current Mesh bounds through the current camera; static registration-time points are invalid when camera or particles move."
    }
  },
  "roles": [
    "module",
    "element",
    "control",
    "text",
    "image",
    "layer"
  ],
  "runtime_adapters": [
    "createDomAdapter",
    "createCanvasAdapter",
    "createCanvasIdBufferAdapter",
    "createThreeRaycastAdapter",
    "createSplatAdapter"
  ],
  "runtime_api": "window.__LOOT_SCENE__.v2",
  "runtime_kinds": [
    "dom",
    "canvas",
    "three",
    "splat",
    "custom"
  ],
  "schema_version": "loot_scene_authoring.v5",
  "selection_contract_schema_version": "selection_contract.v1",
  "selection_modes": [
    "direct",
    "aggregate",
    "proxy",
    "none"
  ]
}
```
