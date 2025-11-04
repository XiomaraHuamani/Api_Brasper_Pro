from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Role, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68,
        min_length=6,
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        max_length=68,
        min_length=6,
        write_only=True,
        required=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "type_identity_document",
            "document_number",
            "country_code",
            "phone_number",
            "marital_status",
            "occupation", 
            "country",
            "city",
            "province",
            "work_situation",
        ]
        extra_kwargs = {
            "country_code": {"required": True},
            "phone_number": {"required": True},
            "email": {"required": True},
            "type_identity_document": {"required": False},
            "document_number": {"required": False},
            "country": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "is_verified": {"read_only": True},
            "marital_status": {"required": False},
            "occupation": {"required": False},
            "work_situation": {"required": False},
        }

    def validate(self, attrs):
        password = attrs.get("password", "")
        password2 = attrs.pop("password2", "")

        if password != password2 and password2 != "":
            raise serializers.ValidationError(
                {"password": "Las contraseñas deben coincidir"}
            )

        return attrs

    def validate_email(self, value):
        # Si es actualización, validar que el email no lo tenga otro usuario
        if self.instance:
            other_user = (
                User.objects.filter(email=value).exclude(id=self.instance.id).first()
            )
            if other_user:
                raise serializers.ValidationError("El email ya está registrado")
        # Si es creación
        else:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("El email ya está registrado")
        return value

    def validate_document_number(self, value):
        if not value:
            return value
            
        if len(value) < 5:
            raise serializers.ValidationError("El número de documento debe tener al menos 5 caracteres")

        # Obtener ID del usuario actual
        instance = getattr(self, 'instance', None)
        if instance:
            # Excluir el usuario actual de la validación
            exists = User.objects.exclude(pk=instance.pk).filter(document_number=value).exists()
        else:
            exists = User.objects.filter(document_number=value).exists()

        if exists:
            raise serializers.ValidationError("El número de documento ya está registrado")

        return value
    
    def create(self, validated_data):
        email = validated_data.get("email")

        try:
            # Obtener el rol de cliente por nombre
            default_role = Role.objects.get(name="client")

            user = User.objects.create_user(
                username=email,
                email=email,
                password=validated_data["password"],
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
                document_number=validated_data.get("document_number", ""),
                country_code=validated_data["country_code"],
                country=validated_data.get("country", ""),
                marital_status=validated_data.get("marital_status", ""),
                occupation=validated_data.get("occupation", ""),
                work_situation=validated_data.get("work_situation", ""),
                phone_number=validated_data.get("phone_number"),
                is_verified=True,
            )

            # Asignar el rol por defecto
            user.role = default_role
            user.save()

            return user
        except Role.DoesNotExist:
            raise serializers.ValidationError("Error: No se encontró el rol de cliente")
        except Exception as e:
            raise serializers.ValidationError(str(e))


class UserPersonalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "type_identity_document",
            "document_number",
            "marital_status",
            "occupation",
            "work_situation",
        ]


class StaffRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68,
        min_length=6,
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        max_length=68,
        min_length=6,
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    role_name = serializers.CharField(read_only=True, source="role.get_name_display")

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "password2",
            "first_name",
            "last_name",
            "role_name",
            "is_verified",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "groups",
            "user_permissions",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "is_verified": {"read_only": True},
            "is_active": {"read_only": True},
            "is_staff": {"read_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
            "groups": {"read_only": True},
            "user_permissions": {"read_only": True},
        }

    def validate(self, attrs):
        password = attrs.get("password", "")
        password2 = attrs.pop("password2", "")

        if password != password2:
            raise serializers.ValidationError(
                {"password": "Las contraseñas deben coincidir"}
            )

        return attrs

    def validate_email(self, value):
        # Si está actualizando (hay una instancia), no validar el email
        if self.context.get("request") and self.context["request"].method == "PUT":
            return value

        # Solo validar en creación
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está registrado")
        return value

    def create(self, validated_data):
        email = validated_data.get("email")

        try:
            staff_role = Role.objects.get(id=1)  # o Role.objects.get(name='staff')

            user = User.objects.create_user(
                username=email,
                email=email,
                password=validated_data["password"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                is_verified=True,
            )

            user.role = staff_role
            user.is_staff = True
            user.save()

            return user
        except Role.DoesNotExist:
            raise serializers.ValidationError("Error: No se encontró el rol staff")
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("username", None)

        # Información básica del usuario
        data.update(
            {
                "full_name": f"{instance.first_name} {instance.last_name}",
                "is_verified": instance.is_verified,
                "is_active": instance.is_active,
                "is_staff": instance.is_staff,
                "date_joined": instance.date_joined,
                "last_login": instance.last_login,
            }
        )

        # Información del rol
        if instance.role:
            data["role"] = {
                "id": instance.role.id,
                "name": instance.role.name,
                "display_name": instance.role.get_name_display(),
            }

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise serializers.ValidationError(
                "Las credenciales proporcionadas son inválidas"
            )

        if not user.is_verified:
            raise serializers.ValidationError("La cuenta no está verificada")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer para obtener la información del usuario"""
    password = serializers.CharField(
        max_length=68,
        min_length=6,
        #write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "type_identity_document",
            "document_number",
            "country_code",
            "phone_number",
            "marital_status",
            "occupation",
            "country",
            "city",
            "province",
            "work_situation",
        ]
        read_only_fields = ("id", "is_verified")
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)  # Cifra la contraseña antes de guardarla
            user.save()
        return user
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Cifra la nueva contraseña
        instance.save()
        return instance


from rest_framework import serializers
from .models import User, Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserFormSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='role', write_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'role', 'role_id',
            'phone_number', 'is_verified'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance



# Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "created_at"]
        read_only_fields = ["created_at"]

    def validate_name(self, value):
        if value not in [Role.STAFF, Role.CLIENT]:
            raise serializers.ValidationError(
                f"El rol debe ser '{Role.STAFF}' o '{Role.CLIENT}'"
            )
        return value

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    frontend_url = serializers.URLField()
