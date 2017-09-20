# -*- coding: utf-8 -*-
'''
:codeauthor: :email:`Agnes Tevesz <agnes.tevesz@morganstanley.com>`

Tests for virtual machine related functions in salt.utils.vmware
'''

# Import python libraries
from __future__ import absolute_import
import logging

# Import Salt testing libraries
from tests.support.unit import TestCase, skipIf
from tests.support.mock import NO_MOCK, NO_MOCK_REASON, patch, MagicMock

from salt.exceptions import VMwareRuntimeError, VMwareApiError, ArgumentValueError

# Import Salt libraries
import salt.utils.vmware as vmware

# Import Third Party Libs
try:
    from pyVmomi import vim, vmodl
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

# Get Logging Started
log = logging.getLogger(__name__)

# Get Logging Started
log = logging.getLogger(__name__)


@skipIf(NO_MOCK, NO_MOCK_REASON)
class ConvertToKbTestCase(TestCase):
    '''Tests for converting units'''

    def setUp(self):
        pass

    def test_gb_conversion_call(self):
        self.assertEqual(vmware.convert_to_kb('Gb', 10), {'size': 10485760L, 'unit': 'KB'})

    def test_mb_conversion_call(self):
        self.assertEqual(vmware.convert_to_kb('Mb', 10), {'size': 10240L, 'unit': 'KB'})

    def test_kb_conversion_call(self):
        self.assertEqual(vmware.convert_to_kb('Kb', 10), {'size': 10L, 'unit': 'KB'})

    def test_conversion_bad_input_argument_fault(self):
        self.assertRaises(ArgumentValueError, vmware.convert_to_kb, 'test', 10)


@skipIf(NO_MOCK, NO_MOCK_REASON)
@skipIf(not HAS_PYVMOMI, 'The \'pyvmomi\' library is missing')
@patch('salt.utils.vmware.get_managed_object_name', MagicMock())
@patch('salt.utils.vmware.wait_for_task', MagicMock())
class UpdateVirtualMachineTestCase(TestCase):
    '''Tests for salt.utils.vmware.update_vm'''

    def setUp(self):
        self.mock_task = MagicMock()
        self.mock_config_spec = MagicMock()
        self.mock_vm_update_task = MagicMock(return_value=self.mock_task)
        self.mock_vm_ref = MagicMock(ReconfigVM_Task=self.mock_vm_update_task)

    def test_update_vm_task_call(self):
        vmware.update_vm(self.mock_vm_ref, self.mock_config_spec)
        self.mock_vm_update_task.assert_called_once()

    def test_update_vm_raise_vim_fault(self):
        exception = vim.fault.VimFault()
        exception.msg = 'vim.fault.VimFault'
        self.mock_vm_ref.ReconfigVM_Task = MagicMock(side_effect=exception)
        with self.assertRaises(VMwareApiError) as exc:
            vmware.update_vm(self.mock_vm_ref, self.mock_config_spec)
        self.assertEqual(exc.exception.strerror, 'vim.fault.VimFault')

    def test_destroy_vm_raise_runtime_fault(self):
        exception = vmodl.RuntimeFault()
        exception.msg = 'vmodl.RuntimeFault'
        self.mock_vm_ref.ReconfigVM_Task = MagicMock(side_effect=exception)
        with self.assertRaises(VMwareRuntimeError) as exc:
            vmware.update_vm(self.mock_vm_ref, self.mock_config_spec)
        self.assertEqual(exc.exception.strerror, 'vmodl.RuntimeFault')

    def test_update_vm_wait_for_task(self):
        mock_wait_for_task = MagicMock()
        with patch('salt.utils.vmware.get_managed_object_name',
                   MagicMock(return_value='my_vm')):
            with patch('salt.utils.vmware.wait_for_task', mock_wait_for_task):
                vmware.update_vm(self.mock_vm_ref, self.mock_config_spec)
        mock_wait_for_task.assert_called_once_with(
            self.mock_task, 'my_vm', 'ReconfigureVM Task')


@skipIf(NO_MOCK, NO_MOCK_REASON)
@skipIf(not HAS_PYVMOMI, 'The \'pyvmomi\' library is missing')
@patch('salt.utils.vmware.get_managed_object_name', MagicMock())
@patch('salt.utils.vmware.wait_for_task', MagicMock())
class DeleteVirtualMachineTestCase(TestCase):
    '''Tests for salt.utils.vmware.delete_vm'''

    def setUp(self):
        self.mock_task = MagicMock()
        self.mock_vm_destroy_task = MagicMock(return_value=self.mock_task)
        self.mock_vm_ref = MagicMock(Destroy_Task=self.mock_vm_destroy_task)

    def test_destroy_vm_task_call(self):
        vmware.delete_vm(self.mock_vm_ref)
        self.mock_vm_destroy_task.assert_called_once()

    def test_destroy_vm_raise_vim_fault(self):
        exception = vim.fault.VimFault()
        exception.msg = 'vim.fault.VimFault'
        self.mock_vm_ref.Destroy_Task = MagicMock(side_effect=exception)
        with self.assertRaises(VMwareApiError) as exc:
            vmware.delete_vm(self.mock_vm_ref)
        self.assertEqual(exc.exception.strerror, 'vim.fault.VimFault')

    def test_destroy_vm_raise_runtime_fault(self):
        exception = vmodl.RuntimeFault()
        exception.msg = 'vmodl.RuntimeFault'
        self.mock_vm_ref.Destroy_Task = MagicMock(side_effect=exception)
        with self.assertRaises(VMwareRuntimeError) as exc:
            vmware.delete_vm(self.mock_vm_ref)
        self.assertEqual(exc.exception.strerror, 'vmodl.RuntimeFault')

    def test_destroy_vm_wait_for_task(self):
        mock_wait_for_task = MagicMock()
        with patch('salt.utils.vmware.get_managed_object_name',
                   MagicMock(return_value='my_vm')):
            with patch('salt.utils.vmware.wait_for_task', mock_wait_for_task):
                vmware.delete_vm(self.mock_vm_ref)
        mock_wait_for_task.assert_called_once_with(
            self.mock_task, 'my_vm', 'Destroy Task')


@skipIf(NO_MOCK, NO_MOCK_REASON)
@skipIf(not HAS_PYVMOMI, 'The \'pyvmomi\' library is missing')
@patch('salt.utils.vmware.get_managed_object_name', MagicMock())
class UnregisterVirtualMachineTestCase(TestCase):
    '''Tests for salt.utils.vmware.unregister_vm'''

    def setUp(self):
        self.mock_vm_unregister = MagicMock()
        self.mock_vm_ref = MagicMock(UnregisterVM=self.mock_vm_unregister)

    def test_unregister_vm_task_call(self):
        vmware.unregister_vm(self.mock_vm_ref)
        self.mock_vm_unregister.assert_called_once()

    def test_unregister_vm_raise_vim_fault(self):
        exception = vim.fault.VimFault()
        exception.msg = 'vim.fault.VimFault'
        self.mock_vm_ref.UnregisterVM = MagicMock(side_effect=exception)
        with self.assertRaises(VMwareApiError) as exc:
            vmware.unregister_vm(self.mock_vm_ref)
        self.assertEqual(exc.exception.strerror, 'vim.fault.VimFault')

    def test_unregister_vm_raise_runtime_fault(self):
        exception = vmodl.RuntimeFault()
        exception.msg = 'vmodl.RuntimeFault'
        self.mock_vm_ref.UnregisterVM = MagicMock(side_effect=exception)
        with self.assertRaises(VMwareRuntimeError) as exc:
            vmware.unregister_vm(self.mock_vm_ref)
        self.assertEqual(exc.exception.strerror, 'vmodl.RuntimeFault')
