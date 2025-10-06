import { useState } from 'react';
import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar } from '@/components/ui/calendar';
import { ComputerEquipmentFormData, EQUIPMENT_TYPES, REQUIRED_FIELDS, ValidationResult } from '@/types/form';
import { getMissingRequiredFields, getFieldLabel } from '@/utils/formUtils';
import { Upload, FileText, CheckCircle2, AlertCircle, Info, Plus, X, CalendarIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EquipmentFormProps {
  formData: ComputerEquipmentFormData;
  onChange: (field: keyof ComputerEquipmentFormData, value: string | number | boolean | Array<unknown>) => void;
  onSubmit: () => void;
  highlightedFields: string[];
  isHighlightAnimating: Record<string, boolean>;
  validationResult?: ValidationResult;
}

const EquipmentForm: React.FC<EquipmentFormProps> = ({
  formData,
  onChange,
  onSubmit,
  highlightedFields,
  isHighlightAnimating,
  validationResult
}) => {
  const missingFields = getMissingRequiredFields(formData);
  const isFormComplete = missingFields.length === 0;

  // ตรวจสอบว่าฟิลด์นั้นเป็น required หรือไม่
  const isRequired = (fieldName: keyof ComputerEquipmentFormData): boolean => {
    return REQUIRED_FIELDS.includes(fieldName);
  };

  // ฟังก์ชันจัดการ equipments array - Fixed dropdown binding
  const addEquipment = () => {
    const newEquipments = [...formData.equipments, { type: '' as ComputerEquipmentFormData['equipments'][0]['type'], quantity: 1, detail: '' }];
    onChange('equipments', newEquipments);
  };

  const removeEquipment = (index: number) => {
    const newEquipments = formData.equipments.filter((_, i) => i !== index);
    onChange('equipments', newEquipments);
  };

  const updateEquipment = (index: number, field: 'type' | 'quantity' | 'detail', value: string | number) => {
    const newEquipments = [...formData.equipments];
    newEquipments[index] = { ...newEquipments[index], [field]: value };
    onChange('equipments', newEquipments);
  };

  // Custom Date Picker Component
  const DatePicker = ({ 
    value, 
    onChange, 
    placeholder = "เลือกวันที่",
    disabled = false 
  }: { 
    value: string; 
    onChange: (date: string) => void; 
    placeholder?: string;
    disabled?: boolean;
  }) => {
    const [open, setOpen] = useState(false);
    const selectedDate = value ? new Date(value) : undefined;

    return (
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "w-full justify-start text-left font-normal",
              !value && "text-muted-foreground",
              disabled && "opacity-50 cursor-not-allowed"
            )}
            disabled={disabled}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {value ? format(new Date(value), "dd/MM/yyyy") : placeholder}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={(date) => {
              if (date) {
                onChange(format(date, "yyyy-MM-dd"));
                setOpen(false);
              }
            }}
            initialFocus
            className={cn("p-3 pointer-events-auto")}
          />
        </PopoverContent>
      </Popover>
    );
  };

  const renderField = (
    fieldName: keyof ComputerEquipmentFormData,
    label: string,
    component: React.ReactNode,
    tooltip?: string
  ) => {
    const required = isRequired(fieldName);
    const isHighlighted = highlightedFields.includes(fieldName);
    const isAnimating = isHighlightAnimating[fieldName];
    const isMissing = missingFields.includes(fieldName);
    const hasValidationError = validationResult?.errors[fieldName];
    
    return (
      <div 
        className={cn(
          "space-y-2 transition-all duration-300",
          isHighlighted && !isAnimating && "ring-2 ring-blue-400 ring-opacity-50 rounded-lg p-2 bg-blue-50/30",
          isAnimating && "animate-highlight-flash rounded-lg p-2"
        )} 
        id={`field-${fieldName}`}
      >
        <div className="flex items-center gap-2">
          <Label htmlFor={fieldName} className="flex items-center gap-2">
            {label}
            {required && <span className="text-red-500 text-lg font-bold">*</span>}
            {tooltip && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Info className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs">{tooltip}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </Label>
          {isHighlighted && (
            <Badge variant="secondary" className="bg-blue-100 text-blue-700 text-xs">
              อัปเดตโดย AI
            </Badge>
          )}
        </div>
        <div className={`${isMissing || hasValidationError ? 'ring-2 ring-red-400 ring-opacity-50 rounded-lg' : ''}`}>
          {component}
        </div>
        {(isMissing || hasValidationError) && (
          <p className="text-sm text-red-500 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {hasValidationError || 'ข้อมูลนี้จำเป็นต้องกรอก'}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col max-h-screen">
      <div className="flex-1 overflow-y-auto bg-gray-50 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
        <div className="p-6 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            แบบฟอร์มขอยืมครุภัณฑ์คอมพิวเตอร์
          </h1>
          <div className="flex items-center justify-center gap-2">
            {isFormComplete ? (
              <>
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span className="text-green-600 font-medium">ข้อมูลครบถ้วนแล้ว</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-5 h-5 text-orange-500" />
                <span className="text-orange-600 font-medium">
                  ข้อมูลไม่ครบ {missingFields.length} ช่อง
                </span>
              </>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-2">
            <span className="text-red-500 font-bold">*</span> = ช่องที่จำเป็นต้องกรอก
          </p>
        </div>

        {/* Section 1: ผู้บันทึก */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-blue-800">1. ข้อมูลผู้บันทึก</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {renderField('employeeId', 'รหัสพนักงาน', 
                <Input
                  id="employeeId"
                  value={formData.employeeId}
                  onChange={(e) => onChange('employeeId', e.target.value)}
                  placeholder="กรอกรหัสพนักงาน"
                />
              )}
              
              {renderField('fullName', 'ชื่อ-สกุล', 
                <Input
                  id="fullName"
                  value={formData.fullName}
                  onChange={(e) => onChange('fullName', e.target.value)}
                  placeholder="กรอกชื่อ-สกุล"
                />
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {renderField('position', 'ตำแหน่ง',
                <Input
                  id="position"
                  value={formData.position}
                  onChange={(e) => onChange('position', e.target.value)}
                  placeholder="กรอกตำแหน่ง"
                />
              )}
              
              {renderField('department', 'ภาควิชา/สถาน/ศูนย์ฝ่าย',
                <Input
                  id="department"
                  value={formData.department}
                  onChange={(e) => onChange('department', e.target.value)}
                  placeholder="กรอกภาควิชา/สถาน/ศูนย์ฝ่าย"
                />
              )}
              
              {renderField('division', 'สาขา/งาน',
                <Input
                  id="division"
                  value={formData.division}
                  onChange={(e) => onChange('division', e.target.value)}
                  placeholder="กรอกสาขา/งาน"
                />
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {renderField('unit', 'หน่วย',
                <Input
                  id="unit"
                  value={formData.unit}
                  onChange={(e) => onChange('unit', e.target.value)}
                  placeholder="กรอกหน่วย"
                />
              )}
              
              {renderField('phoneNumber', 'เบอร์โทรศัพท์', 
                <Input
                  id="phoneNumber"
                  value={formData.phoneNumber}
                  onChange={(e) => onChange('phoneNumber', e.target.value)}
                  placeholder="0812345678"
                />, 
                "เบอร์โทรศัพท์สำหรับติดต่อกลับ รูปแบบ 0XXXXXXXXX"
              )}
              
              {renderField('email', 'อีเมล',
                <Input
                  id="email"
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => onChange('email', e.target.value)}
                  placeholder="example@company.com"
                />
              )}
            </div>
          </CardContent>
        </Card>

        {/* Section 2: รายละเอียดการยืม */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-blue-800">2. รายละเอียดการยืม</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {renderField('subject', 'เรื่อง',
              <Input
                id="subject"
                value={formData.subject}
                onChange={(e) => onChange('subject', e.target.value)}
                placeholder="กรอกเรื่องที่ต้องการยืม"
              />, 
              "หัวข้อหรือเรื่องของการขอยืมอุปกรณ์"
            )}

            {/* Enhanced Dynamic Equipment Section with fixed dropdown binding */}
            {renderField('equipments', 'รายการอุปกรณ์ที่ต้องการยืม',
              <div className="space-y-4">
                {formData.equipments.map((equipment, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-white">
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-medium text-gray-700">อุปกรณ์ที่ {index + 1}</span>
                      {formData.equipments.length > 1 && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => removeEquipment(index)}
                          className="text-red-600 hover:text-red-800"
                          aria-label={`ลบอุปกรณ์ ${equipment.type || 'รายการ'} ${index + 1}`}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label>ประเภทอุปกรณ์</Label>
                          <Select 
                            value={equipment.type || ''} 
                            onValueChange={(value) => updateEquipment(index, 'type', value)}
                          >
                            <SelectTrigger className={equipment.type === '' ? 'text-gray-400' : ''}>
                              <SelectValue placeholder="เลือกประเภทอุปกรณ์" />
                            </SelectTrigger>
                            <SelectContent>
                              {EQUIPMENT_TYPES.map((type) => (
                                <SelectItem key={type} value={type}>
                                  {type}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>จำนวน</Label>
                          <Input
                            type="number"
                            min="1"
                            max="50"
                            value={equipment.quantity === 0 ? '' : equipment.quantity}
                            onChange={(e) => updateEquipment(index, 'quantity', parseInt(e.target.value) || 1)}
                            placeholder="จำนวน"
                          />
                        </div>
                      </div>
                      <div>
                        <Label>รายละเอียดอุปกรณ์</Label>
                        <Input
                          value={equipment.detail || ''}
                          onChange={(e) => updateEquipment(index, 'detail', e.target.value)}
                          placeholder="ระบุรุ่น/ยี่ห้อ (ถ้ามี)"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  onClick={addEquipment}
                  className="w-full"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  เพิ่มอุปกรณ์
                </Button>
              </div>,
              "รายการอุปกรณ์ที่ต้องการยืม สามารถเพิ่มหลายรายการได้"
            )}

            {renderField('borrowingPurpose', 'วัตถุประสงค์ในการยืม',
              <Textarea
                id="borrowingPurpose"
                value={formData.borrowingPurpose}
                onChange={(e) => onChange('borrowingPurpose', e.target.value)}
                placeholder="อธิบายวัตถุประสงค์ในการยืม"
                rows={3}
              />, 
              "อธิบายเหตุผล/วัตถุประสงค์ในการขอยืมอุปกรณ์"
            )}

            <Separator />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-4">
                <h4 className="font-medium text-gray-700">วันที่และเวลาเริ่มใช้งาน</h4>
                <div className="grid grid-cols-2 gap-2">
                  {renderField('usageStartDate', 'วันที่เริ่ม',
                    <DatePicker
                      value={formData.usageStartDate}
                      onChange={(date) => onChange('usageStartDate', date)}
                      placeholder="เลือกวันที่เริ่มใช้งาน"
                    />, 
                    "วันที่ต้องการเริ่มใช้งานอุปกรณ์"
                  )}
                  
                  {renderField('usageStartTime', 'เวลาเริ่ม',
                    <Input
                      id="usageStartTime"
                      type="time"
                      value={formData.usageStartTime}
                      onChange={(e) => onChange('usageStartTime', e.target.value)}
                    />, 
                    "เวลาที่ต้องการเริ่มใช้งานอุปกรณ์"
                  )}
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-gray-700">วันที่และเวลาสิ้นสุด</h4>
                <div className="grid grid-cols-2 gap-2">
                  {renderField('usageEndDate', 'วันที่สิ้นสุด',
                    <DatePicker
                      value={formData.usageEndDate}
                      onChange={(date) => onChange('usageEndDate', date)}
                      placeholder="เลือกวันที่สิ้นสุดการใช้งาน"
                    />, 
                    "วันที่สิ้นสุดการใช้งานอุปกรณ์"
                  )}
                  
                  {renderField('usageEndTime', 'เวลาสิ้นสุด',
                    <Input
                      id="usageEndTime"
                      type="time"
                      value={formData.usageEndTime}
                      onChange={(e) => onChange('usageEndTime', e.target.value)}
                    />, 
                    "เวลาที่สิ้นสุดการใช้งานอุปกรณ์"
                  )}
                </div>
              </div>
            </div>

            {renderField('installationLocation', 'สถานที่ที่ต้องการติดตั้ง',
              <Input
                id="installationLocation"
                value={formData.installationLocation}
                onChange={(e) => onChange('installationLocation', e.target.value)}
                placeholder="เช่น ห้อง A304, อาคาร 1 ชั้น 3"
              />, 
              "ระบุสถานที่ที่ต้องการติดตั้งหรือใช้งานอุปกรณ์"
            )}

            <Separator />

            <div className="space-y-4">
              <h4 className="font-medium text-gray-700">การติดตั้งซอฟต์แวร์</h4>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="defaultSoftware"
                  checked={formData.defaultSoftware}
                  onCheckedChange={(checked) => onChange('defaultSoftware', checked)}
                />
                <Label htmlFor="defaultSoftware">ใช้ซอฟต์แวร์ต้นฉบับ</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="additionalSoftwareNeeded"
                  checked={formData.additionalSoftwareNeeded}
                  onCheckedChange={(checked) => onChange('additionalSoftwareNeeded', checked)}
                />
                <Label htmlFor="additionalSoftwareNeeded">ต้องการโปรแกรมเพิ่มเติม</Label>
              </div>

              {formData.additionalSoftwareNeeded && (
                renderField('additionalSoftwareDetail', 'รายละเอียดโปรแกรมเพิ่มเติม',
                  <Textarea
                    id="additionalSoftwareDetail"
                    value={formData.additionalSoftwareDetail || ''}
                    onChange={(e) => onChange('additionalSoftwareDetail', e.target.value)}
                    placeholder="ระบุโปรแกรมที่ต้องการติดตั้งเพิ่มเติม"
                    rows={2}
                  />
                )
              )}
            </div>
          </CardContent>
        </Card>

        {/* Section 3: ผู้ประสานงาน */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-blue-800">3. ข้อมูลผู้ประสานงาน</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {renderField('coordinatorName', 'ชื่อผู้ประสานงาน',
                <Input
                  id="coordinatorName"
                  value={formData.coordinatorName}
                  onChange={(e) => onChange('coordinatorName', e.target.value)}
                  placeholder="กรอกชื่อผู้ประสานงาน"
                />, 
                "ชื่อบุคคลที่ทำหน้าที่ประสานงานกับเจ้าหน้าที่ IT"
              )}
              
              {renderField('coordinatorPhone', 'เบอร์โทรผู้ประสานงาน',
                <Input
                  id="coordinatorPhone"
                  value={formData.coordinatorPhone}
                  onChange={(e) => onChange('coordinatorPhone', e.target.value)}
                  placeholder="0812345678"
                />, 
                "เบอร์โทรศัพท์ของผู้ประสานงาน"
              )}
            </div>

            {renderField('receiverName', 'ผู้รับอุปกรณ์',
              <Input
                id="receiverName"
                value={formData.receiverName}
                onChange={(e) => onChange('receiverName', e.target.value)}
                placeholder="กรอกชื่อผู้รับอุปกรณ์"
              />, 
              "ชื่อบุคคลที่จะเป็นผู้รับอุปกรณ์จริง"
            )}

            <div className="space-y-4">
              <h4 className="font-medium text-gray-700">วันที่และเวลารับอุปกรณ์</h4>
              <div className="grid grid-cols-2 gap-2">
                {renderField('pickupDate', 'วันที่รับอุปกรณ์',
                  <DatePicker
                    value={formData.pickupDate}
                    onChange={(date) => onChange('pickupDate', date)}
                    placeholder="เลือกวันที่รับอุปกรณ์"
                  />, 
                  "วันที่ต้องการรับอุปกรณ์"
                )}
                
                {renderField('pickupTime', 'เวลารับอุปกรณ์',
                  <Input
                    id="pickupTime"
                    type="time"
                    value={formData.pickupTime}
                    onChange={(e) => onChange('pickupTime', e.target.value)}
                  />, 
                  "เวลาที่ต้องการรับอุปกรณ์"
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Section 4: ข้อมูลเพิ่มเติม */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg text-blue-800">4. ข้อมูลเพิ่มเติม</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {renderField('remarks', 'หมายเหตุ',
              <Textarea
                id="remarks"
                value={formData.remarks || ''}
                onChange={(e) => onChange('remarks', e.target.value)}
                placeholder="ข้อมูลเพิ่มเติม (ถ้ามี)"
                rows={3}
              />
            )}

            <div className="space-y-2">
              <Label>ไฟล์แนบ</Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                <p className="text-sm text-gray-500 mb-2">
                  อัพโหลดไฟล์แนบ (PDF, JPG, PNG, DOCX)
                </p>
                <input
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png,.docx"
                  className="hidden"
                  id="file-upload"
                  onChange={(e) => {
                    const files = Array.from(e.target.files || []);
                    onChange('attachedFiles', files);
                  }}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  เลือกไฟล์
                </Button>
              </div>
              
              {formData.attachedFiles && formData.attachedFiles.length > 0 && (
                <div className="space-y-1">
                  {formData.attachedFiles.map((file, index) => (
                    <div key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                      <FileText className="w-4 h-4" />
                      <span>{file.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Submit Button with Tooltip */}
        <div className="flex justify-center pt-4">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div>
                  <Button
                    onClick={onSubmit}
                    disabled={!isFormComplete}
                    className={`px-8 py-4 text-lg font-semibold shadow-lg transition-all duration-200 ${
                      isFormComplete
                        ? 'bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 hover:shadow-xl hover:scale-105 text-white'
                        : 'bg-gray-400 cursor-not-allowed hover:bg-gray-400 text-gray-600'
                    }`}
                    size="lg"
                  >
                    {isFormComplete ? (
                      <>
                        <CheckCircle2 className="w-6 h-6 mr-3" />
                        ส่งฟอร์มยืมอุปกรณ์
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-6 h-6 mr-3" />
                        กรุณากรอกข้อมูลให้ครบถ้วน
                      </>
                    )}
                  </Button>
                </div>
              </TooltipTrigger>
              {!isFormComplete && (
                <TooltipContent>
                  <div className="max-w-xs">
                    <p className="font-medium mb-2">ข้อมูลที่ยังขาดหายไป:</p>
                    <ul className="text-sm space-y-1">
                      {missingFields.slice(0, 5).map(field => (
                        <li key={field}>• {getFieldLabel(field)}</li>
                      ))}
                      {missingFields.length > 5 && (
                        <li>• และอีก {missingFields.length - 5} รายการ</li>
                      )}
                    </ul>
                  </div>
                </TooltipContent>
              )}
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
    </div>
  </div>
  );
};

export default EquipmentForm;