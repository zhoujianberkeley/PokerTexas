# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: dealer.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='dealer.proto',
  package='Dealer',
  syntax='proto3',
  serialized_pb=_b('\n\x0c\x64\x65\x61ler.proto\x12\x06\x44\x65\x61ler\"\xae\x02\n\rDealerRequest\x12\x0c\n\x04user\x18\x01 \x01(\t\x12\r\n\x05token\x18\x02 \x01(\t\x12\x10\n\x08identity\x18\x03 \x01(\t\x12\x0f\n\x07\x63ommand\x18\x04 \x01(\t\x12\x0e\n\x06giveup\x18\x05 \x01(\x05\x12\r\n\x05\x61llin\x18\x06 \x01(\x05\x12\r\n\x05\x63heck\x18\x07 \x01(\x05\x12\x0f\n\x07\x63\x61llbet\x18\x08 \x01(\x05\x12\x10\n\x08raisebet\x18\t \x01(\x05\x12\x0e\n\x06\x61mount\x18\n \x01(\x05\x12\x0b\n\x03pos\x18\x0b \x01(\x05\x12\x0c\n\x04type\x18\x0c \x01(\x05\x12\x0b\n\x03num\x18\r \x01(\x05\x12\x0e\n\x06status\x18\x0e \x01(\x05\x12\x0f\n\x07version\x18\x0f \x01(\t\x12\x11\n\tactionNum\x18\x10 \x01(\x05\x12\x11\n\tuserMoney\x18\x11 \x03(\x05\x12\r\n\x05\x65xtra\x18\x12 \x01(\t2H\n\x04Game\x12@\n\nGameStream\x12\x15.Dealer.DealerRequest\x1a\x15.Dealer.DealerRequest\"\x00(\x01\x30\x01\x62\x06proto3')
)




_DEALERREQUEST = _descriptor.Descriptor(
  name='DealerRequest',
  full_name='Dealer.DealerRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='user', full_name='Dealer.DealerRequest.user', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='token', full_name='Dealer.DealerRequest.token', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='identity', full_name='Dealer.DealerRequest.identity', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='command', full_name='Dealer.DealerRequest.command', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='giveup', full_name='Dealer.DealerRequest.giveup', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='allin', full_name='Dealer.DealerRequest.allin', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='check', full_name='Dealer.DealerRequest.check', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='callbet', full_name='Dealer.DealerRequest.callbet', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='raisebet', full_name='Dealer.DealerRequest.raisebet', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='amount', full_name='Dealer.DealerRequest.amount', index=9,
      number=10, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pos', full_name='Dealer.DealerRequest.pos', index=10,
      number=11, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='Dealer.DealerRequest.type', index=11,
      number=12, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num', full_name='Dealer.DealerRequest.num', index=12,
      number=13, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='Dealer.DealerRequest.status', index=13,
      number=14, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='version', full_name='Dealer.DealerRequest.version', index=14,
      number=15, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='actionNum', full_name='Dealer.DealerRequest.actionNum', index=15,
      number=16, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='userMoney', full_name='Dealer.DealerRequest.userMoney', index=16,
      number=17, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='extra', full_name='Dealer.DealerRequest.extra', index=17,
      number=18, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=25,
  serialized_end=327,
)

DESCRIPTOR.message_types_by_name['DealerRequest'] = _DEALERREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DealerRequest = _reflection.GeneratedProtocolMessageType('DealerRequest', (_message.Message,), dict(
  DESCRIPTOR = _DEALERREQUEST,
  __module__ = 'dealer_pb2'
  # @@protoc_insertion_point(class_scope:Dealer.DealerRequest)
  ))
_sym_db.RegisterMessage(DealerRequest)



_GAME = _descriptor.ServiceDescriptor(
  name='Game',
  full_name='Dealer.Game',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=329,
  serialized_end=401,
  methods=[
  _descriptor.MethodDescriptor(
    name='GameStream',
    full_name='Dealer.Game.GameStream',
    index=0,
    containing_service=None,
    input_type=_DEALERREQUEST,
    output_type=_DEALERREQUEST,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_GAME)

DESCRIPTOR.services_by_name['Game'] = _GAME

try:
  # THESE ELEMENTS WILL BE DEPRECATED.
  # Please use the generated *_pb2_grpc.py files instead.
  import grpc
  from grpc.beta import implementations as beta_implementations
  from grpc.beta import interfaces as beta_interfaces
  from grpc.framework.common import cardinality
  from grpc.framework.interfaces.face import utilities as face_utilities


  class GameStub(object):
    """The greeting service definition.
    """

    def __init__(self, channel):
      """Constructor.

      Args:
        channel: A grpc.Channel.
      """
      self.GameStream = channel.stream_stream(
          '/Dealer.Game/GameStream',
          request_serializer=DealerRequest.SerializeToString,
          response_deserializer=DealerRequest.FromString,
          )


  class GameServicer(object):
    """The greeting service definition.
    """

    def GameStream(self, request_iterator, context):
      """Sends a greeting
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')


  def add_GameServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'GameStream': grpc.stream_stream_rpc_method_handler(
            servicer.GameStream,
            request_deserializer=DealerRequest.FromString,
            response_serializer=DealerRequest.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'Dealer.Game', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class BetaGameServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    """The greeting service definition.
    """
    def GameStream(self, request_iterator, context):
      """Sends a greeting
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetaGameStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    """The greeting service definition.
    """
    def GameStream(self, request_iterator, timeout, metadata=None, with_call=False, protocol_options=None):
      """Sends a greeting
      """
      raise NotImplementedError()


  def beta_create_Game_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('Dealer.Game', 'GameStream'): DealerRequest.FromString,
    }
    response_serializers = {
      ('Dealer.Game', 'GameStream'): DealerRequest.SerializeToString,
    }
    method_implementations = {
      ('Dealer.Game', 'GameStream'): face_utilities.stream_stream_inline(servicer.GameStream),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_Game_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('Dealer.Game', 'GameStream'): DealerRequest.SerializeToString,
    }
    response_deserializers = {
      ('Dealer.Game', 'GameStream'): DealerRequest.FromString,
    }
    cardinalities = {
      'GameStream': cardinality.Cardinality.STREAM_STREAM,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'Dealer.Game', cardinalities, options=stub_options)
except ImportError:
  pass
# @@protoc_insertion_point(module_scope)
