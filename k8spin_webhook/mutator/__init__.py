from flask import Blueprint, request, jsonify
from loguru import logger
import base64
import jsonpatch

from k8spin_common.resources import tenant

blueprint = Blueprint("mutator", __name__, url_prefix="/mutator")

def mutator_response(allowed, message, json_patch):
    base64_patch = None
    if json_patch:
        base64_patch = base64.b64encode(
            json_patch.to_string().encode("utf-8")).decode("utf-8")
    return jsonify({"response": {"allowed": allowed,
                                 "status": {"message": message},
                                 "patchType": "JSONPatch",
                                 "patch": base64_patch}})

@blueprint.route('/organizations', methods=['POST'])
def organization_mutator():
    request_info = request.get_json()
    organization_name = request_info["request"]["object"]["metadata"]["name"]
    patch = jsonpatch.JsonPatch([{"op": "add", "path": "/metadata/labels", "value": {"k8spin.cloud/org": organization_name}}])
    return mutator_response(True, "", patch)

@blueprint.route('/tenants', methods=['POST'])
def tenant_mutator():
    request_info = request.get_json()
    organization_name = request_info["request"]["namespace"].replace("org-", "")
    patch = jsonpatch.JsonPatch([{"op": "add", "path": "/metadata/labels", "value": {"k8spin.cloud/org": organization_name, "k8spin.cloud/tenant": request_info["request"]["name"]}}])
    return mutator_response(True, "", patch)

@blueprint.route('/spaces', methods=['POST'])
def space_mutator():
    request_info = request.get_json()
    parent_tenant = tenant.get_tenant_from_namespace(tenant_namespace_name=request_info["request"]["namespace"])
    parent_organization = parent_tenant.org
    patch = jsonpatch.JsonPatch([{"op": "add", "path": "/metadata/labels", "value": {"k8spin.cloud/org": parent_organization.metadata["name"], "k8spin.cloud/tenant": parent_tenant.metadata["name"], "k8spin.cloud/space": request_info["request"]["name"]}}])
    return mutator_response(True, "", patch)
