from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import send_file, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
import os
from datetime import datetime
from libs import image_helper
from libs.strings import gettext
from schemas.image import ImageSchema
from flask_uploads import UploadSet, IMAGES

IMAGE_SET = UploadSet("images", IMAGES)

image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required
    def post(self):
        """
        This endpoint is used to upload an image file. It uses the
        JWT to retrieve user information and save the image in the user's folder.
        If a file with the same name exists in the user's folder, name conflicts
        will be automatically resolved by appending a underscore and a smallest
        unused integer. (eg. filename.png to filename_1.png).
        """
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            # save(self, storage, folder=None, name=None)
            image_path = image_helper.save_image(data["image"], folder=folder)
            # here we only return the basename of the image and hide the internal folder structure from our user
            basename = image_helper.get_basename(image_path)
            return {"message": gettext("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:  # forbidden file type
            extension = image_helper.get_extension(data["image"])
            return {"message": gettext("image_illegal_extension").format(extension)}, 400


class Image(Resource):
    @jwt_required
    def get(self, filename: str):
        """
        This endpoint returns the requested image if exists. It will use JWT to
        retrieve user information and look for the image inside the user's folder.
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        # check if filename is URL secure
        if not image_helper.is_filename_safe(filename):
            return {"message": gettext("image_illegal_file_name").format(filename)}, 400
        try:
            # try to send the requested file to the user with status code 200
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404

class AvatarUpload(Resource):
    @jwt_required
    def put(self):
        """
        This endpoint is used to upload user avatar. All avatars are named after the user's id
        in such format: user_{id}.{ext}.
        It will overwrite the existing avatar.
        """
        data = image_schema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "avatars"
        existed = image_helper.is_image_existed(folder, get_jwt_identity())
        if existed:
            try:
                os.remove(existed)
            except:
                return {"message": gettext("avatar_delete_failed")}, 500
        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + "_"+ datetime.now().strftime("%m%d%Y_%H%M%S") + ext  # use our naming format + true extension
            avatar_path = image_helper.save_image(
                data["image"], folder=folder, name=avatar
            )
            print(avatar_path)
            basename = image_helper.get_basename(avatar_path)
            return {"message": gettext("avatar_uploaded").format(basename),
                    "image": 'static/images/'+avatar_path}, 200
        except UploadNotAllowed:  # forbidden file type
            extension = image_helper.get_extension(data["image"])
            return {"message": gettext("image_illegal_extension").format(extension)}, 400


class Avatar(Resource):
    @classmethod
    def get(cls, user_id: int):
        """
        This endpoint returns the avatar of the user specified by user_id.
        """
        folder = "avatars"
        avatar = image_helper.is_image_existed(folder,user_id)
        print(avatar)
        if avatar:
            return avatar
        return {"message": gettext("avatar_not_found")}, 404
