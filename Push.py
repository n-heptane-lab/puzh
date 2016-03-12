#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/Push/Push.py
from __future__ import with_statement
import logging
from ableton.v2.base import listens, task
from ableton.v2.control_surface import ControlSurface
from pushbase.control_element_factory import create_sysex_element
from pushbase.sysex import LIVE_MODE, USER_MODE
import Live
import sysex
from handshake_component import HandshakeComponent, make_dongle_message, MinimumFirmwareVersionElement
logger = logging.getLogger(__name__)
HANDSHAKE_DELAY = 1.0

class Push(ControlSurface):
    __module__ == __name__
    __doc__ == "Puzh"

    def __init__(self, *a, **k):
        super(Push, self).__init__(*a, **k)
        with self.component_guard():
            self._suppress_sysex = False
            self._create_components()
            self._mode_change = create_sysex_element(sysex.MODE_CHANGE)
            self._send_midi((144,60,30))
            self._write_line1 = create_sysex_element(sysex.WRITE_LINE1)
#            super(Push,self)._send_midi((240, 71, 127, 21, 98, 0, 1, 0, 247))

#        self.log_message('Push script loaded')
#        logger.info('Handshake succeded with firmware version %.2f!' % self._handshake.firmware_version)
        self.show_message('Push script loaded')

    def _create_components(self):
        self._init_handshake()
#        super(Push, self)._create_components()

    def _init_handshake(self):
        logger.info('entering _init_handshake')
#        self.log_message('_init_handshake')
        dongle_message, dongle = make_dongle_message(sysex.DONGLE_ENQUIRY_PREFIX)
        identity_control = create_sysex_element(sysex.IDENTITY_PREFIX, sysex.IDENTITY_ENQUIRY)
        dongle_control = create_sysex_element(sysex.DONGLE_PREFIX, dongle_message)
        presentation_control = create_sysex_element(sysex.DONGLE_PREFIX, sysex.make_presentation_message(self.application()))
        self._handshake = HandshakeComponent(identity_control=identity_control, dongle_control=dongle_control, presentation_control=presentation_control, dongle=dongle, is_root=True)
        self._on_handshake_success.subject = self._handshake
        self._on_handshake_failure.subject = self._handshake
        self._start_handshake_task = self._tasks.add(task.sequence(task.wait(HANDSHAKE_DELAY), task.run(self._start_handshake)))
        logger.info('leaving _init_handshake')
#        self._start_handshake_task.kill()

    def _start_handshake(self):
        logger.info('_start_handshake')
        self._start_handshake_task.kill()
        self._handshake._start_handshake()

    @listens('success')
    def _on_handshake_success(self):
        logger.info('Handshake succeded with firmware version %.2f!' % self._handshake.firmware_version)
        self.show_message('handshake succeeded.')
        super(Push, self).update()
        self._c_instance.set_firmware_version(self._handshake.firmware_version)
        with self.component_guard():
            self._suppress_sysex = False
            self._mode_change.send_value((LIVE_MODE,))
#            self._write_line1.send_value((82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,
#                                         82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,
#                                         82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,
#                                         82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,82,))
#            self._send_midi(sysex.WELCOME_MESSAGE)

    @listens('failure')
    def _on_handshake_failure(self, bootloader_mode):
        logger.error('Handshake failed, performing harakiri!')
        self.show_message('handshake failed.')
